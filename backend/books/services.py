from .models import Book


def create_book(*, user, data):
    return Book.objects.create(created_by=user, **data)


def delete_book(*, user, book):
    if book.created_by != user:
        raise PermissionError("You cannot delete this book")

    book.delete()