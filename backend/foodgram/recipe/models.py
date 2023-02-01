from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    """Ингредиенты."""

    title = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        help_text='Введите название ингредиента')
    sum = models.DecimalField(
        verbose_name='Количество ингредиента',
        max_digits=10,
        decimal_places=2,
        help_text='Введите количество ингредиента'
    )
    dimension = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения')

    class Meta:
        ordering = ('title',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Теги рецептов."""
    title = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        help_text='Введите название тега')
    color = models.CharField(
        verbose_name='Цвет тега',
        max_length=50,
        help_text='Введите цвет тега')
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
        help_text='Введите слаг')

    class Meta:
        ordering = ('title',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title


class Recipe(models.Model):
    """
    Рецепты пользователей.

    Ключевые аргументы:
    description - описание рецепта
    pub_date - дата публикации
    author - привязка к автору рецепта
    title - название рецепта
    image - картинка рецепта
    cooking_time - время приготовления
    tags - привязка к тегам
    ingredients - привязка к ингредиентам
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        help_text='Автор'
    )
    title = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True,
        help_text='Загрузите картинку'
    )
    description = models.TextField(
        verbose_name='Описание приготовления',
        help_text='Введите описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes',
        help_text='Выберите ингредиенты'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
        help_text='Выберите теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления'
    )


    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:15]