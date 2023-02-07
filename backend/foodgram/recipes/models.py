from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        help_text='Введите название ингредиента')
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Теги рецептов."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
        help_text='Введите название тега')
    color = models.CharField(
        verbose_name='Цвет тега',
        max_length=50,
        unique=True,
        help_text='Введите цвет тега')
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
        help_text='Введите слаг')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Рецепты пользователей.

    Ключевые аргументы:
    description - описание рецепта
    pub_date - дата публикации
    author - привязка к автору рецепта
    name - название рецепта
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
    name = models.CharField(
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
    text = models.TextField(
        verbose_name='Описание приготовления',
        help_text='Введите описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='recipes',
        blank=True,
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


class RecipeIngredient(models.Model):
    """Ингредиенты рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            'Количество ингредиента не должно быть меньше 1'
        )],
        verbose_name='Количество ингредиента',
        help_text='Введите количество ингредиента'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.ingredient.measurement_unit}'
            f'- {self.amount}'
        )

class Favorite(models.Model):
    """Избранное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Список покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_shops'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_shops'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} - {self.recipe}'
