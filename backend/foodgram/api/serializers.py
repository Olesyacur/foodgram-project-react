from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'last_name'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        return value


class UserSerializer(UserSerializer):
    """Сериализатор для получения данных пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if (request and not request.user.is_anonymous):
            return Follow.objects.filter(user=request.user).exists()
        return False


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes_count',
            'recipes',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        author = obj.author
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=author).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj.author)
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов рецепта."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit'
        )


class IngredientFieldSerializer(serializers.ModelSerializer):
    """Сериализатор для введения полей ингредиента при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientFieldSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        """Проверка наличия ингредиентов, тегов, времени приготовления."""

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Необходимо выбрать ингредиент.'
            })

        ingredients_id = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться.'
            })

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Необходимо выбрать тег.'
            })

        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть не меньше 1.'
            })

        return data

    def create_ingredients(self, ingredients, recipe):
        """Создание ингредиентов."""

        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient_id, amount=amount
            )

    def create_tags(self, tags, recipe):
        """Создание тегов."""

        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        """Создание рецепта."""

        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        instance.tags.clear()
        tags = validated_data.get('tags')
        self.create_tags(tags, instance)

        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(ingredients, instance)

        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance, context=context).data


class RecipeFieldSerializer(serializers.ModelSerializer):
    """Сериализатор для получения полей рецепта."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверка наличия рецепта в избранном."""

        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в избранное',
            )
        return data

    def to_representation(self, instance):
        """Получение избранного."""

        return RecipeFieldSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверка наличия рецепта в списке покупок."""

        request = self.context.get('request')
        recipe = data['recipe']
        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в список покупок',
            )
        return data

    def to_representation(self, instance):
        """Получение списка покупок."""

        return RecipeFieldSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
