from books.models import Book
from .models import ReadingList, ReadingListItem


def list_reading_lists_for_user(*, user):
    return (
        ReadingList.objects.filter(user=user)
        .prefetch_related("items__book")
        .order_by("-created_at")
    )


def get_reading_list_by_id(*, reading_list_id):
    return ReadingList.objects.prefetch_related("items__book").get(pk=reading_list_id)


def get_reading_list_item_by_id(*, reading_list, item_id):
    return ReadingListItem.objects.select_related("book", "reading_list").get(
        pk=item_id,
        reading_list=reading_list,
    )


def get_book_by_id(*, book_id):
    return Book.objects.get(pk=book_id)
