"""Add image field to Recipe model."""
import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_ingredients_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(
                null=True,
                upload_to=core.models.recipe_image_file_path,
            ),
        ),
    ]
