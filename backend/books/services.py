import logging

from .models import Book

logger = logging.getLogger(__name__)


def create_book(*, user, data):
    book = Book.objects.create(created_by=user, **data)
    logger.info("Book created: book_id=%s user_id=%s", book.id, user.id)
    return book


def delete_book(*, user, book):
    if book.created_by != user:
        logger.warning(
            "Book delete denied: book_id=%s owner_id=%s actor_id=%s",
            book.id,
            book.created_by_id,
            user.id,
        )
        raise PermissionError("You cannot delete this book")

    book_id = book.id
    book.delete()
    logger.info("Book deleted: book_id=%s user_id=%s", book_id, user.id)
