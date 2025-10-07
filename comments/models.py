from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

User = get_user_model()


class Comment(models.Model):
    """Comments that can be attached to articles,
    revisions, or other content.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        HIDDEN = "hidden", "Hidden"
        DELETED = "deleted", "Deleted"
        FLAGGED = "flagged", "Flagged"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Generic foreign key to allow comments on any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Comment content
    content = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    # Threading support
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    # Status and moderation
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    # Engagement
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "-created_at"]),
            models.Index(fields=["author", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.content_object}"

    @property
    def is_reply(self):
        return self.parent is not None

    @property
    def reply_count(self):
        return self.replies.filter(status=self.Status.ACTIVE).count()

    @property
    def score(self):
        return self.upvotes - self.downvotes

    def get_thread_root(self):
        """Get the root comment of the thread."""
        if self.parent:
            return self.parent.get_thread_root()
        return self

    def get_depth(self):
        """Get nesting depth (0 for root comments)."""
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth


class CommentVote(models.Model):
    """Track user votes on comments."""

    class VoteType(models.TextChoices):
        UP = "up", "Upvote"
        DOWN = "down", "Downvote"

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="votes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_votes"
    )
    vote_type = models.CharField(max_length=4, choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["comment", "user"]
        indexes = [
            models.Index(fields=["comment", "vote_type"]),
        ]

    def __str__(self):
        return (
            f"{self.user.username} {self.vote_type}voted "
            f"comment {self.comment.id}"
        )

    def save(self, *args, **kwargs):
        # Handle vote counting
        if self.pk:
            # Updating existing vote
            old_vote = CommentVote.objects.get(pk=self.pk)
            if old_vote.vote_type != self.vote_type:
                if old_vote.vote_type == self.VoteType.UP:
                    self.comment.upvotes -= 1
                    self.comment.downvotes += 1
                else:
                    self.comment.downvotes -= 1
                    self.comment.upvotes += 1
        else:
            # New vote
            if self.vote_type == self.VoteType.UP:
                self.comment.upvotes += 1
            else:
                self.comment.downvotes += 1

        super().save(*args, **kwargs)
        self.comment.save()

    def delete(self, *args, **kwargs):
        # Adjust vote counts when deleting
        if self.vote_type == self.VoteType.UP:
            self.comment.upvotes -= 1
        else:
            self.comment.downvotes -= 1

        super().delete(*args, **kwargs)
        self.comment.save()
