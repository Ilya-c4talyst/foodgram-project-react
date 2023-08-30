from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import User, Follow
from recipes.models import Recipe
from recipes.constants import recipes_default


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and obj.follow.filter(user=self.context['request'].user).exists()
        )


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()


class RecipeOnFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get(
            'recipes_limit', recipes_default
        )
        recipes_by_author = obj.recipes.all()[:int(limit)]
        return RecipeOnFollowSerializer(
            recipes_by_author, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
                UniqueTogetherValidator(
                    queryset=Follow.objects.all(),
                    fields=('user', 'author'),
                    message='Вы уже подписаны на этого пользователя.'
                )
            ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.')
        return data
