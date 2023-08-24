from django_filters import rest_framework as filters

from .models import Recipe, Tag


class FilterForRecipes(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    is_favorited = filters.NumberFilter(
        field_name='favorites_recipe__user', method='filter_users'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
        )

    def filter_users(self, queryset, name, value):
        if self.request.user.is_authenticated and int(value):
            return queryset.filter({name: self.request.user})
        return queryset
