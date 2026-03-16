from django.db import models
from django.conf import settings
from books.models import Book

User = settings.AUTH_USER_MODEL


class ReadingList(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reading_lists"
    )

    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_reading_list_name_per_user",
            ),
        ]


class ReadingListItem(models.Model):

    reading_list = models.ForeignKey(
        ReadingList,
        on_delete=models.CASCADE,
        related_name="items"
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ["reading_list", "book"]
