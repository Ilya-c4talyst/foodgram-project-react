from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, TagViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]
