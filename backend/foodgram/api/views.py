from django.db import IntegrityError
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import Pagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, UserSerializer, )


class UserViewSet(UserViewSet):
    """Создание и получение данных пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated, ),
        serializer_class=FollowSerializer,
    )
    def subscribe(self, request, **kwargs):
        """Подписка на автора."""
        author = self.get_object()
        user = self.request.user

        if user == author:
            return Response(
                {'message': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            try:
                subscribtion = Follow.objects.create(user=user, author=author)
            except IntegrityError:
                return Response(
                    {'message': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(
                subscribtion,
                context={'request': request},
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=(IsAuthenticated, ))
    def subscriptions(self, request):
        """Получение списка подписок."""
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    pagination_class = None
    search_fields = ('^name', )
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Все действия с рецептами."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def get_permissions(self):
        if self.action in {'get', 'update', 'partial_update', 'destroy'}:
            self.permission_classes = (IsAuthorOrAdminOrReadOnly, )
        if self.action in {'create'}:
            self.permission_classes = (IsAuthenticated, )
    # @action(
    #     detail=True,
    #     methods=('post', 'delete'),
    #     permission_classes=(IsAuthenticated, )
    # )

    def update(self, request, *args, **kwargs):
        if kwargs['partial'] is False:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    #     if self.action in {
    #         'favorite',
    #         'shopping_cart'
    #     }:
    #         self.permission_classes = (IsAuthorOrAdminOrReadOnly, )
    #     return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, **kwargs):
        """Добавление рецепта в избранное или удаление из избранного."""
        try:
            recipe_id = int(self.kwargs.get('pk'))
        except ValueError:
            return Response(
                {
                    'message': (
                        'Рецепт с идентификатором '
                        f'{self.kwargs.get("pk")} не найден'
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )
        recipe = self.get_object()
        data = {
            'recipe': recipe_id,
            'user': request.user.id,
        }

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data=data,
                context={'request': request},)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = Favorite.objects.filter(user=request.user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {'message': 'Рецепт не найден в избранном'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, **kwargs):
        """Добавление рецепта в список покупок или удаление из него."""
        try:
            recipe_id = int(self.kwargs.get('pk'))
        except ValueError:
            return Response(
                {
                    'message': (
                        'Рецепт с идентификатором '
                        f'{self.kwargs.get("pk")} не найден'
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        recipe = get_object_or_404(Recipe, pk=recipe_id)
        data = {
            'recipe': recipe_id,
            'user': request.user.id,
        }

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data=data,
                context={'request': request},)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {'message': 'Рецепт не найден в списке покупок'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=('get', ),
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        """Скачивание ингредиентов из списка покупок."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__favorite_shops__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by()
        )
        shop_list = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount']
            shop_list.append(
                f'\n{name} - {amount} {measurement_unit}')
        result = 'shop_list.txt'
        response = HttpResponse(
            shop_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={result}'
        return response
