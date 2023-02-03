from rest_framework import viewsets
from django.db.models import Sum
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import Follow, User
from recipes.models import Recipe, Ingredient, Tag, Favorite, ShoppingCart, RecipeIngredient

from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    FollowSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    RecipeCreateSerializer
)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthor
from .pagination import Pagination


class UserViewSet(UserViewSet):
    """Создание и получение данных пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination
 
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Подписка на автора"""
        author = get_object_or_404(User, id=id)
        user = request.user
        
        if request.method == 'POST':
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={'request': request},
            )
            Follow.objects.get_or_create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    def subscriptions(self, request):
        """Получение списка подписок"""
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    pagination_class = None
    filter_backends = (IngredientFilter,)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вывод рецептов"""
    quereset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthor,)
    filter_backends = (RecipeFilter,)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer
    
class FavoriteViewSet(viewsets.ModelViewSet):
    """Добавление рецептов в избранное"""
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = self.request.user
        
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe,
                data=request.data,
                context={'request': request},
            )
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Добавление рецептов в корзину"""
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = self.request.user
        
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                recipe,
                data=request.data,
                context={'request': request},
            )
            ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивание ингридиентов из списка покупок"""
        ingredients = RecipeIngredient.objects.filter(recipe__shopping_cart__user=request.user).values('ingredient__name', 'ingredient__measurement_unit').annotate(amount=Sum('amount')).order_by()
        