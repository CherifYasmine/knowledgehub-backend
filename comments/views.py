from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Comment
from .serializers import CommentSerializer
from .serializers import ContentTypeSerializer
from django.contrib.contenttypes.models import ContentType


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model."""

    queryset = Comment.objects.all().select_related("author", "content_type")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["author", "content_type", "object_id", "status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """List available ContentType entries (id, app_label, model).

    Useful for clients that need the numeric ContentType id to create
    GenericForeignKey-based objects like comments.
    """

    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
    permission_classes = [permissions.AllowAny]
