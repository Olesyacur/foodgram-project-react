from rest_framework import viewsets
from django.db.models import Sum
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import Follow, User
from recipes.models import Recipe, Ingredient, Tag, Favorite, ShoppingCart, RecipeIngredient

from .serializers import (
    UserSerializer,
    FollowSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    RecipeCreateSerializer
)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .pagination import Pagination


class UserViewSet(UserViewSet):
    """Создание и получение данных пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination
 
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        serializer_class=FollowSerializer,
    )
    def subscribe(self, request, **kwargs):
        """Подписка на автора"""
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.request.user
        
        if user == author:
            return Response(
                {'message': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            subscribtion, _ = Follow.objects.get_or_create(user=user, author=author)
            serializer = self.get_serializer(
                subscribtion,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, permission_classes=[IsAuthenticated])
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
    search_fields = ('^name', )
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Все действия с рецептами"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def get_permissions(self):
        if self.action in [
            'favorite'
        ]:
            self.permission_classes = [IsAuthorOrAdminOrReadOnly]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        #recipe = get_object_or_404(Recipe, id=id)
        context = {'request': request}
        data = {
            'recipe': pk,
            'user': request.user.id,
        }
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    @favorite.mapping.delete    
    def favorite_delete(self, request, pk):
        object = get_object_or_404(
            Favorite,
            user=request.user,
            recipe = get_object_or_404(Recipe, id=pk)
        )
        if object.exist():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'message': 'Нет такого рецепта в списке избранного'},
            status=status.HTTP_400_BAD_REQUEST
        )


    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, id):
        """Добавление в список покупок"""
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
    
    def shopping_list(ingredients):
        """Создание списка покупок"""
        shop_list = {}
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount']
            shop_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }
        result = 'shop_list.txt'
        response = HttpResponse(
            shop_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={result}'
        return response

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивание ингридиентов из списка покупок"""
        ingredients = RecipeIngredient.objects.filter(recipe__shopping_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(amount=Sum('amount')).order_by()
        return self.shopping_list(ingredients)
        