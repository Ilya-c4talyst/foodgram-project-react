from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from djoser.views import UserViewSet

from recipes.pagination import CustomPagination
from .models import User, Follow
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    FollowSerializer,
    FollowCreateSerializer
)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = CustomPagination

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(
    #     detail=True, methods=['post', 'delete'],
    #     permission_classes=[permissions.IsAuthenticated]
    # )
    # def subscribe(self, request, pk=None):
    #     user_to_subscribe = self.get_object()
    #     if user_to_subscribe == request.user:
    #         return Response(
    #             {'error': 'Невозможно подписаться на себя же.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     follow, created = Follow.objects.get_or_create(
    #         user=request.user, author=user_to_subscribe
    #     )
    #     if request.method == 'DELETE':
    #         follow.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     serializer = FollowCreateSerializer(
    #         follow, context={'request': request}
    #     )
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class = FollowSerializer
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = self.get_object()
        if request.method == 'POST':
            data = {
            'user': user.id,
            'author': id
            }
            subscription = FollowCreateSerializer(data=data)
            subscription.is_valid(raise_exception=True)
            subscription.save()
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            instance = user.follower.filter(author=author)
            if not instance:
                raise ValidationError(
                    {
                        'errors': [
                            'Вы не подписаны на этого автора'
                        ]
                    }
                )
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )


    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=FollowSerializer
    )
    def subscriptions(self, request):
        def queryset():
            return User.objects.filter(follow__user=self.request.user)
        self.get_queryset = queryset
        return self.list(request)
