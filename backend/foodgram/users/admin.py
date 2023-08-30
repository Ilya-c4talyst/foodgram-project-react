from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import User, Follow


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'pk', 'username', 'email',
        'password', 'first_name', 'last_name'
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_editable = ('user', 'author')


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
 