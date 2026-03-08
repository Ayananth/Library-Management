from .models import Book


def list_books():
    return Book.objects.select_related("created_by").order_by("-created_at")


def get_book_by_id(*, book_id):
    return Book.objects.select_related("created_by").get(pk=book_id)
