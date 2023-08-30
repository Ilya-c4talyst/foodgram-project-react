from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from .models import (
    Ingredient, Tag, IngredientsInRecipe,
    Recipe, Favorites, ShoppingCart
)
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipeSaveSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        read_only=True,
        source='recipes'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and obj.favorites_recipe.filter(
                user=self.context['request'].user
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and obj.shopping_cart_recipe.filter(
                user=self.context['request'].user
            ).exists()
        )


class CreateShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')
    image = Base64ImageField(source='recipe.image')

    class Meta:
        model = Favorites
        fields = ('id', 'name', 'image', 'cooking_time')


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'


class FavoriteCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShopCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class IngredientRecipeCreateSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Необходимо указать тег/теги.'
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо указать ингредиенты.'
            )
        return ingredients

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def to_representation(self, value):
        return RecipeSerializer(value, context=self.context).data

    def create_ingredients(self, recipe, ingredients_data):
        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id'].id
            amount = ingredient_data['amount']
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            ingredients.append(IngredientsInRecipe(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            ))
        IngredientsInRecipe.objects.bulk_create(ingredients)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag_data in tags_data:
            recipe.tags.add(tag_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients_data)
        return instance
