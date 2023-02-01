from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Пользователи проекта с ролями:
        Аноним,
        Аутентифицированный пользователь,
        Администратор.
    """

    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Аутентифицированный пользователь'),
        (ADMIN, 'Администратор'),
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
        null=False,
    )
    username = models.CharField(
        verbose_name='Ник пользователя',
        max_length=150,
        null=False,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=254
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    def __str__(self):
        return self.username

    
