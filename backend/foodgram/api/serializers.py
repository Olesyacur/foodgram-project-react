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
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'username', 'first_name', 'last_name', 'recipes_count', 'recipes')
        read_only_fields = ('username', 'first_name', 'last_name', 'email')
    
    def validate(self, obj):
        user = self.context.get('request').user
        author_id = self.context.get('kwargs').get('pk')
        author = get_object_or_404(User, id=author_id)
        if user == author:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого автора',
                code=status.HTTP_400_BAD_REQUEST,
            )        
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()


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
        source='ingredient.id',
        write_only=True,
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
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
        if request is None:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,)
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
 
    def create_ingredients(recipe, ingredients):
        """Создание ингредиентов с учетом их количества по рецепту"""
        ingredient_new_list = []
        for ingredient_new in ingredients:
            ingredient_new_list.append(
                RecipeIngredient(
                    ingredient = Ingredient.objects.get(
                        id=ingredient_new['id']),
                    amount = ingredient_new['amount'],
                    recipe = recipe,
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_new_list)
    
    def create(self, validated_data):
        """Создание рецепта"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
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
    
    #def to_representation(self, instance):
     #   """Получение рецепта"""
      #  return RecipeSerializer(instance).data


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
