from django.contrib import admin

from .models import (
    Ingredient, Tag, Recipe,
    Favorites, ShoppingCart, IngredientsInRecipe
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    model = IngredientsInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'display_ingredients', 'in_favorites')
    list_editable = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = [
        IngredientInline,
    ]

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        ingredients_list = ', '.join([ingredient.ingredient.name for ingredient in obj.ingredients.all() if ingredient.ingredient.name])
        return ingredients_list

    @admin.display(description='Избранное')
    def in_favorites(self, obj):
        return obj.favorites_recipe.count()


@admin.register(IngredientsInRecipe)
class IngredientsInRecipe(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(Favorites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
