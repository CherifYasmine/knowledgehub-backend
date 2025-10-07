from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model."""

    queryset = Comment.objects.all().select_related("author", "content_type")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["author", "content_type", "status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
