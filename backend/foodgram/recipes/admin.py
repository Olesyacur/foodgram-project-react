from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)

admin.site.unregister(Group)


class RecipeInIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    fields = ('ingredient', 'amount')
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'get_author',
        'name',
        'text',
        'get_ingredients',
        'get_tags',
        'cooking_time',
        'count_favorite',)
    list_filter = ('name', 'author', 'tags',)
    search_fields = (
        'name',
        'author__email',
        'tags__name',
        'ingredients__name',)
    inlines = (RecipeInIngredientAdmin,)
    readonly_fields = ('count_favorite',)

    @admin.display(description='Автор')
    def get_author(self, obj):
        return obj.author.username

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join([
            ingredient.name for ingredient in obj.ingredients.all()])

    @admin.display(description='Количество избранного')
    def count_favorite(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')
