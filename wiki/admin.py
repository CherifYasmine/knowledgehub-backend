from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Category,
    Article,
    Revision,
    Section,
    ArticleCollaborator,
    ArticleView,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "article_count", "created_at"]
    list_filter = ["parent", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}

    def article_count(self, obj):
        return obj.articles.count()

    article_count.short_description = "Articles"


class RevisionInline(admin.TabularInline):
    model = Revision
    extra = 0
    readonly_fields = ["version_number", "created_at"]
    fields = [
        "version_number",
        "title",
        "change_message",
        "editor",
        "created_at",
    ]


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ["title", "order", "parent"]


class ArticleCollaboratorInline(admin.TabularInline):
    model = ArticleCollaborator
    extra = 0


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "status",
        "category",
        "author",
        "featured",
        "view_count",
        "revision_count_display",
        "updated_at",
    ]
    list_filter = ["status", "featured", "category", "created_at"]
    search_fields = ["title", "current_content", "author__username"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["view_count", "created_at", "updated_at"]

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "title",
                    "slug",
                    "current_content",
                    "current_summary",
                )
            },
        ),
        (
            "Classification",
            {"fields": ("status", "category", "tags", "featured")},
        ),
        ("Authorship", {"fields": ("author", "last_editor")}),
        (
            "Analytics",
            {
                "fields": ("view_count", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [RevisionInline, SectionInline, ArticleCollaboratorInline]

    def revision_count_display(self, obj):
        count = obj.revision_count
        if count > 0:
            base_url = reverse("admin:wiki_revision_changelist")
            url = f"{base_url}?article__id__exact={obj.id}"
            return format_html('<a href="{}">{} revisions</a>', url, count)
        return "0 revisions"

    revision_count_display.short_description = "Revisions"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category", "author", "last_editor")
        )


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = [
        "article",
        "version_number",
        "title",
        "editor",
        "is_current_display",
        "created_at",
    ]
    list_filter = ["created_at", "editor"]
    search_fields = ["article__title", "title", "content", "change_message"]
    readonly_fields = ["version_number", "created_at"]

    fieldsets = (
        ("Article", {"fields": ("article",)}),
        ("Content", {"fields": ("title", "content", "summary", "tags")}),
        (
            "Change Info",
            {
                "fields": (
                    "version_number",
                    "change_message",
                    "editor",
                    "created_at",
                )
            },
        ),
    )

    def is_current_display(self, obj):
        if obj.is_current:
            return format_html('<span style="color: green;">✓ Current</span>')
        return format_html('<span style="color: gray;">Old</span>')

    is_current_display.short_description = "Status"

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("article", "editor")
        )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["title", "article", "parent", "order", "level_display"]
    list_filter = ["article", "created_at"]
    search_fields = ["title", "content", "article__title"]

    def level_display(self, obj):
        level = obj.get_level()
        indent = "— " * level
        return format_html("{}Level {}", indent, level)

    level_display.short_description = "Level"

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("article", "parent")
        )


@admin.register(ArticleCollaborator)
class ArticleCollaboratorAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "article",
        "permission",
        "invited_by",
        "created_at",
    ]
    list_filter = ["permission", "created_at"]
    search_fields = [
        "user__username",
        "article__title",
        "invited_by__username",
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "article", "invited_by")
        )


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ["article", "user", "ip_address", "viewed_at"]
    list_filter = ["viewed_at"]
    search_fields = ["article__title", "user__username", "ip_address"]
    readonly_fields = ["viewed_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("article", "user")
