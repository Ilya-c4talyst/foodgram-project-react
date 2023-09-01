from rest_framework import pagination

from .constants import PAGE_SIZE_RECIPE, MAX_PAGE_SIZE_RECIPE


class CustomPagination(pagination.PageNumberPagination):
    page_size = PAGE_SIZE_RECIPE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE_RECIPE
