# Generated by Django 4.1.5 on 2023-02-02 18:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_favoriteshop_favorite'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FavoriteShop',
            new_name='ShoppingCart',
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='dimension',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='title',
            new_name='name',
        ),
    ]
