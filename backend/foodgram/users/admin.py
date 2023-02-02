from django.contrib import admin

# Register your models here.
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'last_name', 'first_name')
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'last_name')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
