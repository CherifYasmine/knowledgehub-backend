from django.contrib import admin
from django.utils.html import format_html
from .models import Comment, CommentVote


class CommentVoteInline(admin.TabularInline):
    model = CommentVote
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "content_preview",
        "author",
        "content_object_display",
        "status",
        "score_display",
        "reply_count_display",
        "created_at",
    ]
    list_filter = ["status", "created_at", "content_type"]
    search_fields = ["content", "author__username"]
    readonly_fields = ["upvotes", "downvotes", "created_at", "updated_at"]

    fieldsets = (
        ("Content", {"fields": ("content", "status")}),
        (
            "Relationship",
            {"fields": ("content_type", "object_id", "parent", "author")},
        ),
        (
            "Engagement",
            {"fields": ("upvotes", "downvotes"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "edited_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [CommentVoteInline]

    def content_preview(self, obj):
        content = obj.content[:100]
        if len(obj.content) > 100:
            content += "..."
        return content

    content_preview.short_description = "Content"

    def content_object_display(self, obj):
        if obj.content_object:
            return format_html(
                "{}: {}",
                obj.content_type.name.title(),
                str(obj.content_object)[:50],
            )
        return "None"

    content_object_display.short_description = "On"

    def score_display(self, obj):
        score = obj.score
        color = "green" if score > 0 else "red" if score < 0 else "gray"
        return format_html('<span style="color: {};">{}</span>', color, score)

    score_display.short_description = "Score"

    def reply_count_display(self, obj):
        count = obj.reply_count
        if count > 0:
            return format_html("{} replies", count)
        return "No replies"

    reply_count_display.short_description = "Replies"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author", "content_type", "parent")
        )


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ["comment_preview", "user", "vote_type", "created_at"]
    list_filter = ["vote_type", "created_at"]
    search_fields = ["comment__content", "user__username"]
    readonly_fields = ["created_at"]

    def comment_preview(self, obj):
        content = obj.comment.content[:50]
        if len(obj.comment.content) > 50:
            content += "..."
        return content

    comment_preview.short_description = "Comment"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("comment", "user")
