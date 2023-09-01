from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from djoser.views import UserViewSet

from recipes.pagination import CustomPagination
from .models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    FollowSerializer,
    FollowCreateSerializer
)


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.all()

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ],
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = self.get_object()
        if request.method == 'POST':
            data = {
                'user': user.id,
                'author': id
            }
            subscribe = FollowCreateSerializer(data=data)
            subscribe.is_valid(raise_exception=True)
            subscribe.save()
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscribe, _ = user.follower.filter(author=author).delete()
            if not subscribe:
                raise ValidationError(
                    {
                        'errors': [
                            'Отсутствует подписка на автора'
                        ]
                    }
                )
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=FollowSerializer
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(follow__user=self.request.user)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FollowSerializer(
            result_page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
