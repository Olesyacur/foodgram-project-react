from django.contrib import admin

# Register your models here.
from .models import Recipe, Ingredient, Tag, RecipeIngredient
from django.contrib.auth.models import Group

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.unregister(Group)


class RecipeInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 0  
    min_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.validate_min = True
        return formset

    @admin.display(description='Ингредиенты')
    def ingredients(self, obj):
        return ', '.join([
            ingredient.title for ingredient in obj.ingredients.all()])



#admin.site.register(RecipeIngredient)

