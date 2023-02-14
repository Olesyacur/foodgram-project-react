# Generated by Django 4.1.5 on 2023-02-14 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipeingredient_options_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite'),
        ),
    ]