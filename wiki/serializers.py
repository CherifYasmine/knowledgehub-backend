from rest_framework import serializers
from .models import Article, Section, Revision


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model."""

    author_name = serializers.CharField(
        source="author.get_full_name", read_only=True
    )
    total_sections = serializers.IntegerField(
        source="sections.count", read_only=True
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "current_content",
            "current_summary",
            "author",
            "author_name",
            "status",
            "featured",
            "total_sections",
            "current_revision",
            "category",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
            "current_revision",
            "author",
        ]

    def create(self, validated_data):
        # Set the author to the current user
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section model."""

    section_level = serializers.CharField(source="get_level", read_only=True)
    section_number = serializers.CharField(
        source="get_section_number", read_only=True
    )

    class Meta:
        model = Section
        fields = [
            "id",
            "article",
            "title",
            "content",
            "order",
            "parent",
            "section_level",
            "section_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "section_level",
            "section_number",
            "created_at",
            "updated_at",
        ]


class RevisionSerializer(serializers.ModelSerializer):
    """Serializer for Revision model."""

    editor_name = serializers.CharField(
        source="editor.get_full_name", read_only=True
    )

    class Meta:
        model = Revision
        fields = [
            "id",
            "article",
            "version_number",
            "title",
            "content",
            "summary",
            "editor",
            "editor_name",
            "change_message",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "version_number",
            "created_at",
            "updated_at",
            "editor",
        ]

    def create(self, validated_data):
        # Set the editor to the current user
        validated_data["editor"] = self.context["request"].user
        return super().create(validated_data)
