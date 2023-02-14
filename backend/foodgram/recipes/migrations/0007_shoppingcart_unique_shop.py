# Generated by Django 4.1.5 on 2023-02-14 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_favorite_unique_favorite'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shop'),
        ),
    ]
