# Generated by Django 3.2.16 on 2023-08-31 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230829_0051'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientsinrecipe',
            options={'verbose_name': 'Ингредиенты в рецепте', 'verbose_name_plural': 'Ингредиенты в рецепте'},
        ),
    ]