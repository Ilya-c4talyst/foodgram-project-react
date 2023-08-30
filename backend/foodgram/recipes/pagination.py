from rest_framework import pagination

from .constants import page_size_recipe, max_page_size_recipe


class CustomPagination(pagination.PageNumberPagination):
    page_size = page_size_recipe
    page_size_query_param = 'page_size'
    max_page_size = max_page_size_recipe
