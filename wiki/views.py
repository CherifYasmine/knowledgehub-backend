from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Article, Section, Revision
from .serializers import (
    ArticleSerializer,
    SectionSerializer,
    RevisionSerializer,
)
from comments.models import Comment
from comments.serializers import CommentSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for Article model."""

    queryset = (
        Article.objects.all()
        .select_related("author")
        .prefetch_related("sections")
    )
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "featured", "author"]
    search_fields = ["title", "current_content", "current_summary"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    @extend_schema(
        summary="Get article comments",
        description="Retrieve all comments for a specific article",
    )
    @action(detail=True, methods=["get"])
    def comments(self, request, slug=None):
        """Get all comments for an article."""
        from django.contrib.contenttypes.models import ContentType

        article = self.get_object()
        content_type = ContentType.objects.get_for_model(Article)
        comments = Comment.objects.filter(
            content_type=content_type, object_id=article.id
        ).select_related("author")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get article revisions",
        description="Retrieve all revisions for a specific article",
    )
    @action(detail=True, methods=["get"])
    def revisions(self, request, slug=None):
        """Get all revisions for an article."""
        article = self.get_object()
        revisions = article.revisions.all().select_related("author")
        serializer = RevisionSerializer(revisions, many=True)
        return Response(serializer.data)


class SectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Section model."""

    queryset = Section.objects.all().select_related("article")
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["article"]
    ordering_fields = ["order", "created_at"]
    ordering = ["order"]


class RevisionViewSet(viewsets.ModelViewSet):
    """ViewSet for Revision model."""

    queryset = Revision.objects.all().select_related("article", "editor")
    serializer_class = RevisionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["article", "editor"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
