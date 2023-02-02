from django.contrib import admin

# Register your models here.
from .models import Recipe, Ingredient, Tag, RecipeIngredient, Favorite, ShoppingCart
from django.contrib.auth.models import Group

admin.site.unregister(Group)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
       'author', 'name', 'text' ,'ingredients', 'tags', 'cooking_time')
    list_filter = ('tags',)
    search_fields = ('name',)
    inlines = (RecipeIngredientAdmin,)

    @admin.display(description='Теги')
    def tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def ingredients(self, obj):
        return ', '.join([
            ingredient.name for ingredient in obj.ingredients.all()])


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


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

#admin.site.register(Recipe)
#admin.site.register(Ingredient)
#admin.site.register(Tag)
#admin.site.register(RecipeIngredient)

