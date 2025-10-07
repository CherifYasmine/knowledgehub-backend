from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()


class BaseModel(models.Model):
    """Base model with common fields for all wiki models."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    """Categories for organizing articles."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Hex color code for category",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_full_path(self):
        """Get the full category path (parent > child)."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Article(BaseModel):
    """Main article model with versioning support."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    # Current version fields (for quick access)
    current_content = models.TextField(blank=True)
    current_summary = models.TextField(
        max_length=500, blank=True, help_text="Brief summary of the article"
    )

    # Metadata
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    tags = models.JSONField(default=list, blank=True)

    # Authorship and permissions
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_articles"
    )
    last_editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="edited_articles",
    )

    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)

    # Revision tracking
    current_revision = models.OneToOneField(
        "Revision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_for_article",
    )

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "featured"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["-updated_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def increment_view_count(self):
        """Increment view count atomically."""
        Article.objects.filter(id=self.id).update(
            view_count=models.F("view_count") + 1
        )

    def get_absolute_url(self):
        """Get the article URL."""
        return f"/articles/{self.slug}/"

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def revision_count(self):
        return self.revisions.count()


class Revision(BaseModel):
    """Article revision for version control."""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="revisions"
    )
    version_number = models.PositiveIntegerField()

    # Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(
        max_length=500, blank=True, help_text="Brief summary of the article"
    )

    # Change tracking
    change_message = models.TextField(
        blank=True, help_text="Description of what changed in this revision"
    )
    editor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="revisions"
    )

    # Metadata from article at time of revision
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-version_number"]
        unique_together = ["article", "version_number"]
        indexes = [
            models.Index(fields=["article", "-version_number"]),
        ]

    def __str__(self):
        return f"{self.article.title} v{self.version_number}"

    def save(self, *args, **kwargs):
        if not self.version_number:
            # Auto-increment version number
            last_revision = (
                Revision.objects.filter(article=self.article)
                .order_by("-version_number")
                .first()
            )

            self.version_number = (
                last_revision.version_number + 1 if last_revision else 1
            )

        super().save(*args, **kwargs)

        # Update article's current fields
        self.article.current_content = self.content
        self.article.current_summary = self.summary
        self.article.title = self.title
        self.article.tags = self.tags
        self.article.last_editor = self.editor
        self.article.current_revision = self
        self.article.save()

    @property
    def is_current(self):
        return self.article.current_revision == self


class Section(BaseModel):
    """Sections within articles for better organization."""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    # Optional parent section for nested structure
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subsections",
    )

    class Meta:
        ordering = ["order", "title"]
        unique_together = ["article", "order"]

    def __str__(self):
        return f"{self.article.title} - {self.title}"

    def get_level(self):
        """Get nesting level (0 for top-level)."""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def get_section_number(self):
        """Get hierarchical section numbering."""
        if self.parent:
            parent_num = self.parent.get_section_number()
            siblings = Section.objects.filter(
                article=self.article, parent=self.parent
            ).order_by("order")

            for i, section in enumerate(siblings, 1):
                if section.id == self.id:
                    return f"{parent_num}.{i}"
        else:
            siblings = Section.objects.filter(
                article=self.article, parent__isnull=True
            ).order_by("order")

            for i, section in enumerate(siblings, 1):
                if section.id == self.id:
                    return str(i)
        return "1"


class ArticleCollaborator(BaseModel):
    """Track users who can collaborate on articles."""

    class Permission(models.TextChoices):
        VIEW = "view", "View Only"
        EDIT = "edit", "Edit"
        ADMIN = "admin", "Admin"

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="collaborators"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="article_collaborations"
    )
    permission = models.CharField(
        max_length=10, choices=Permission.choices, default=Permission.VIEW
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_collaborations",
    )

    class Meta:
        unique_together = ["article", "user"]

    def __str__(self):
        return (
            f"{self.user.username} - {self.article.title} ({self.permission})"
        )


class ArticleView(models.Model):
    """Track article views for analytics."""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="article_views"
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["article", "-viewed_at"]),
            models.Index(fields=["-viewed_at"]),
        ]

    def __str__(self):
        return f"View: {self.article.title} at {self.viewed_at}"
