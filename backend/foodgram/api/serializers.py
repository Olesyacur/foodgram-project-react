from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from users.models import Follow, User
from recipes.models import Recipe, Ingredient, Tag, Favorite, ShoppingCart, RecipeIngredient
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class UserSerializer(UserSerializer):
    """Сериализатор для получения данных пользователя"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок"""
    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

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
            'is_subscribed')
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False     
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj.author)
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSerializer(recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов рецепта"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True,
    )
    amount = serializers.IntegerField(write_only=True, min_value=1)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'recipe')
        extra_kwargs = {'amount': {'min_value': None}}


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients', read_only=True)
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
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False
        
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
        return False
        


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text', 'ingredients', 'tags', 'cooking_time')

    def valid_ingredients(self, ingredients):
        """Проверка наличия ингредиентов"""
        if not ingredients:
            raise serializers.ValidationError(
                detail='Необходимо добавить ингридиенты',
            )
        return ingredients

    def valid_tags(self, tags):
        """Проверка наличия тегов"""
        if not Tag.objects.filter(id=tags.id).exists():
            raise serializers.ValidationError(
                detail='Тег не найден',
            )
        return tags
 
    def create_ingredients(self, recipe, ingredients):
        """Создание ингредиентов с учетом их количества по рецепту"""
        ingredient_new_list = []
        
        for ingredient in ingredients:
            ingredient_new_list.append(
                RecipeIngredient(
                    ingredient = Ingredient.objects.get(
                        id=ingredient['ingredient'].id
                    ),
                    amount = ingredient['amount'],
                    recipe = recipe,
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_new_list)
    
    def create(self, validated_data):
        """Создание рецепта"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        request = self.context.get('request')
        recipe = Recipe.objects.create(
            author=request.user, **validated_data)
        recipe.tags.add(*tags)

        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tags.clear()
        instance.tags.add(*tags)
        instance.ingredients.clear()
        recipe = instance
        self.create_ingredients(recipe, ingredients)
        instance.save()
        
        return instance
    
    def to_representation(self, instance):
        """Получение рецепта"""
        representation = super().to_representation(instance)
        representation['ingredients'] = RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=instance).all(),
            many=True
        ).data
        return representation

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
    )
    recipe = RecipeSerializer(read_only=True)
    recipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        source='recipe',
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        """Проверка наличия рецепта в избранном"""
        if Favorite.objects.filter(user=data['user'], recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в избранное',
            )
        return data

    def to_representation(self, instance):
        """Получение избранного"""
        return FavoriteSerializer(instance).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверка наличия рецепта в списке покупок"""
        if ShoppingCart.objects.filter(user=data['user'], recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в список покупок',
            )
        return data

    def to_representation(self, instance):
        """Получение списка покупок"""
        return ShoppingCartSerializer(instance).data
