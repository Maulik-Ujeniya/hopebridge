from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPreference


class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'Preferences'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [UserPreferenceInline]
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {
            'fields': ('profile_picture', 'phone', 'country', 'city', 'pincode', 'full_address')
        }),
        ('HopeBridge', {
            'fields': ('role', 'is_profile_complete')
        }),
    )
