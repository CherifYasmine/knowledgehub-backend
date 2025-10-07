from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with additional fields for the knowledge hub."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="User's role in the system",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    bio = models.TextField(blank=True, help_text="User's bio or description")
    avatar = models.URLField(
        blank=True, help_text="URL to user's avatar image"
    )

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_editor(self):
        return self.role in [self.Role.ADMIN, self.Role.EDITOR]

    @property
    def can_edit(self):
        """Check if user can edit content."""
        return self.is_editor

    @property
    def can_admin(self):
        """Check if user has admin privileges."""
        return self.is_admin
