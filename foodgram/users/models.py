from django.db import models
from django.db.models import Q, F
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.contrib.auth.models import AbstractUser

from .validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150, unique=True, validators=[validate_username]
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow'
    )

    class Meta:
        ordering = ['user']
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'], name='unique_user_author'
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='user_not_equal_author'
            ),
        ]
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} - {self.author}'
