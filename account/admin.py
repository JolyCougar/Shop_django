from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': (
                'agreement_accepted',
                'email_verified',
                'cookies_accepted',
                'bio',
                'avatar',
            )
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': (
                'agreement_accepted',
                'email_verified',
                'cookies_accepted',
                'bio',
                'avatar',
            )
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />',
                               obj.avatar.url)
        return "Аватарки нет"

    avatar_preview.short_description = 'Avatar Preview'
    list_display = ('username', 'first_name', 'email', 'avatar_preview')


admin.site.register(CustomUser, CustomUserAdmin)
