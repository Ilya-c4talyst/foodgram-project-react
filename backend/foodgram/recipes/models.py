from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField

from .constants import rc_len, max_time, min_time, max_amount, min_amount


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=rc_len)
    measurement_unit = models.CharField(max_length=rc_len)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'], name='unique_ingredient'
        )]

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(max_length=rc_len)
    color = ColorField(default='#FF0000', unique=True)
    slug = models.SlugField(max_length=rc_len, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=rc_len)
    text = models.TextField()
    image = models.ImageField(upload_to='recipes/', blank=True)
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                min_time, message='Слишком маленькое значение!'
            ),
            MaxValueValidator(max_time, message='Слишком большое значение!')
        ],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
    )
    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ['name',]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                min_amount, message='Слишком маленькое значение!'
            ),
            MaxValueValidator(max_amount, message='Слишком большое значение!')
        ],
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'], name='unique_ingredient_recipe'
        )]
        verbose_name = 'Ингредиенты в рецепте'

    def __str__(self):
        return (
            f'{self.recipe}: {self.ingredient}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name='unique_shop'
        )]
        verbose_name = 'Покупной лист'
        verbose_name_plural = 'Покупной лист'

    def __str__(self):
        return f'{self.user} --> {self.recipe}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name='unique_favor'
        )]
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'

    def __str__(self):
        return f'{self.user} <--> {self.recipe}'
    

# class BaseRelationModel(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE
#     )

#     class Meta:
#         abstract = True


# class ShoppingCart(BaseRelationModel):
#     Recipe.related_query_name = 'shopping_cart_recipes'

#     class Meta:
#         constraints = [models.UniqueConstraint(
#             fields=['recipe', 'user'], name='unique_user_recipe'
#         )]
#         verbose_name = 'Покупной лист'
#         verbose_name_plural = 'Покупной лист'


#     def __str__(self):
#         return f'{self.user} --> {self.recipe}'


# class Favorites(BaseRelationModel):
#     Recipe.related_query_name = 'favorite_recipes'

#     class Meta:
#         constraints = [models.UniqueConstraint(
#             fields=['recipe', 'user'], name='unique_user_recipe_favor'
#         )]
#         verbose_name = 'Рецепт в избранном'
#         verbose_name_plural = 'Рецепты в избранном'

#     def __str__(self):
#         return f'{self.user} <--> {self.recipe}'

