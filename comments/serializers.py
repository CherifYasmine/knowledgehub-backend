from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model.

    The `author` is set automatically from `request.user` during create().
    Clients should not supply `author` in the POST payload.
    """

    author_name = serializers.CharField(
        source="author.get_full_name", read_only=True
    )
    content_object_str = serializers.CharField(
        source="__str__", read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "content_type",
            "object_id",
            "content_object_str",
            "content",
            "author",
            "author_name",
            "parent",
            "status",
            "upvotes",
            "downvotes",
            "created_at",
            "updated_at",
            "edited_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "edited_at",
            "author",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if (
            request
            and hasattr(request, "user")
            and request.user.is_authenticated
        ):
            validated_data["author"] = request.user
        return super().create(validated_data)


class ContentTypeSerializer(serializers.Serializer):
    """Read-only serializer for django ContentType entries."""

    id = serializers.IntegerField(read_only=True)
    app_label = serializers.CharField(read_only=True)
    model = serializers.CharField(read_only=True)
