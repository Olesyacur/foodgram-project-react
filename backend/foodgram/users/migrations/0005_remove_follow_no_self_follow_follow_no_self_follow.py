# Generated by Django 4.1.5 on 2023-02-13 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_follow_no_self_follow_follow_no_self_follow'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='no_self_follow',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(('user', models.F('author')), _negated=True), name='no_self_follow'),
        ),
    ]
