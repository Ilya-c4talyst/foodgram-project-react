from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

from .models import (
    Ingredient, Tag, Recipe, Favorites, ShoppingCart, IngredientsInRecipe
)
from .permissions import IsAuthorOrAdminOnlyPermission
from .filters import FilterForRecipes
from .pagination import CustomPagination
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    FavoriteCreateSerializer, ShopCreateSerializer,
    RecipeCreateUpdateSerializer, FavoriteSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', '^name')


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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        if self.action == 'favorite':
            return FavoriteCreateSerializer
        if self.action == 'shopping_cart':
            return ShopCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (permissions.AllowAny,)
        elif self.action in ('favorite', 'shopping_cart'):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.request.method in (
            'PATCH', 'DELETE'
        ):
            self.permission_classes = (IsAuthorOrAdminOnlyPermission,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            favorite, created = Favorites.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                return Response(
                    {'detail': 'Рецепт добавлен в избранное!'},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'detail': 'Рецепт уже есть в избранном!'},
                status=status.HTTP_200_OK
            )
        elif request.method == 'DELETE':
            Favorites.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт удалён из избранного!'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
            detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated]
    )
    def favorites(self, request):
        favorites = Favorites.objects.filter(user=request.user)
        serializer = FavoriteSerializer(
            favorites, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            shop_item, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                return Response(
                    {'detail': 'Рецепт добавлен в корзину!'},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'detail': 'Рецепт уже в корзине!'},
                status=status.HTTP_200_OK
            )
        elif request.method == 'DELETE':
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(
                {'detail': 'Рецепт удалён из корзины'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        shopping_list = ShoppingCart.objects.filter(user=request.user)
        recipe_ids = shopping_list.values_list('recipe_id', flat=True)
        recipes = Recipe.objects.filter(id__in=recipe_ids)

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
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
