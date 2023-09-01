from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

from .models import (
    Ingredient, Tag, Recipe, Favorites, ShoppingCart, IngredientsInRecipe
)
from .permissions import IsAuthorOrReadOnlyPermission
from .filters import FilterForRecipes, IngredientFilter
from .pagination import CustomPagination
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    FavoriteCreateSerializer, ShopCreateSerializer,
    RecipeCreateUpdateSerializer, FavoriteSerializer, CreateShowSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForRecipes
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrReadOnlyPermission, ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return super().get_serializer_class()

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = self.get_object()
        if request.method == 'POST':
            data = {
                'user': user.id,
                'recipe': pk
            }
            serializer = FavoriteCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = CreateShowSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted_count, _ = user.favorites_user.filter(
                recipe=recipe
            ).delete()
            if not deleted_count:
                raise serializers.ValidationError(
                    {
                        'errors': [
                            'Рецепт отсутствует в избранном'
                        ]
                    }
                )
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorites(self, request):
        favorites = Favorites.objects.filter(user=request.user)
        serializer = FavoriteSerializer(
            favorites, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            user = request.user
            if ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = {'user': user.id, 'recipe': pk}
            serializer = ShopCreateSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = CreateShowSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            deleted_count, _ = ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            if not deleted_count:
                return Response(
                    {'errors': 'Рецепта нет в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        content = self.generate_shopping_cart_content(request.user)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    def generate_shopping_cart_content(self, user):
        shopping_list = ShoppingCart.objects.filter(user=user)
        recipe_ids = shopping_list.values_list('recipe_id', flat=True)
        recipes = Recipe.objects.filter(id__in=recipe_ids)
        content = self.generate_shopping_list_text(recipes)
        return content

    def generate_shopping_list_text(self, recipes):
        content = ''
        for recipe in recipes:
            content += f'{recipe.name}\n'
            ingredients_in_recipe = IngredientsInRecipe.objects.filter(
                recipe=recipe
            )
            for ingredient in ingredients_in_recipe:
                content += (
                    f'{ingredient.ingredient.name} '
                    f'({ingredient.ingredient.measurement_unit}) '
                    f'— {ingredient.amount}\n'
                )
            content += '\n'
        return content
