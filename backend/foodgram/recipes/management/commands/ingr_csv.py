import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from a CSV file'

    def handle(self, *args, **options):
        file_name = 'ingredients.csv'
        file_path = os.path.join('recipes', 'management', file_name)
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                name = row[0]
                measurement_unit = row[1]
                ingredient = Ingredient(
                    name=name, measurement_unit=measurement_unit
                )
                ingredient.save()

        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены!'))
