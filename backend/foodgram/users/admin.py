from django.contrib import admin

from users.models import User, Follow

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'last_name', 'first_name')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    empty_value_display = '-пусто-'
