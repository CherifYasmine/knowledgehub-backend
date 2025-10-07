from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""

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
        read_only_fields = ["id", "created_at", "updated_at", "edited_at"]

    def create(self, validated_data):
        # Set the author to the current user
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
