from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""

    # Add role to the list display
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )
    search_fields = ("username", "first_name", "last_name", "email")

    # Add custom fields to the user form
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional Info",
            {"fields": ("role", "bio", "avatar", "created_at", "updated_at")},
        ),
    )

    # Make timestamp fields read-only
    readonly_fields = ("created_at", "updated_at")

    # Add role to the add user form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
