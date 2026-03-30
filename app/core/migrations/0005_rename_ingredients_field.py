"""
Migration to rename Recipe.Ingredients → Recipe.ingredients.

Rationale: Django field names must use snake_case. The original field
was named 'Ingredients' (PascalCase) which is a Django anti-pattern
and caused issues at the serializer layer.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20260209_2116'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='Ingredients',
            new_name='ingredients',
        ),
    ]
