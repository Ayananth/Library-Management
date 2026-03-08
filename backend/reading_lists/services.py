from django.db import transaction
from django.db.models import F, Max

from .models import ReadingList, ReadingListItem


def create_reading_list(*, user, name):
    return ReadingList.objects.create(user=user, name=name)


def update_reading_list(*, reading_list, name):
    reading_list.name = name
    reading_list.save(update_fields=["name"])
    return reading_list


def delete_reading_list(*, reading_list):
    reading_list.delete()


def ensure_reading_list_owner(*, user, reading_list):
    if reading_list.user_id != user.id:
        raise PermissionError("You cannot access this reading list.")


@transaction.atomic
def add_book_to_reading_list(*, reading_list, book, order=None):
    if ReadingListItem.objects.filter(reading_list=reading_list, book=book).exists():
        raise ValueError("This book already exists in the reading list.")

    max_order = (
        ReadingListItem.objects.filter(reading_list=reading_list).aggregate(max_order=Max("order"))["max_order"]
        or 0
    )

    if order is None:
        target_order = max_order + 1
    else:
        if order < 1:
            raise ValueError("Order must be 1 or higher.")

        if order > max_order + 1:
            raise ValueError(f"Order cannot be greater than {max_order + 1}.")

        ReadingListItem.objects.filter(reading_list=reading_list, order__gte=order).update(
            order=F("order") + 1
        )
        target_order = order

    return ReadingListItem.objects.create(
        reading_list=reading_list,
        book=book,
        order=target_order,
    )


@transaction.atomic
def remove_item_from_reading_list(*, reading_list_item):
    reading_list = reading_list_item.reading_list
    removed_order = reading_list_item.order

    reading_list_item.delete()

    ReadingListItem.objects.filter(reading_list=reading_list, order__gt=removed_order).update(
        order=F("order") - 1
    )


@transaction.atomic
def reorder_reading_list_item(*, reading_list_item, new_order):
    reading_list = reading_list_item.reading_list
    old_order = reading_list_item.order

    total_items = ReadingListItem.objects.filter(reading_list=reading_list).count()
    if new_order < 1 or new_order > total_items:
        raise ValueError(f"Order must be between 1 and {total_items}.")

    if new_order == old_order:
        return reading_list_item

    if new_order < old_order:
        ReadingListItem.objects.filter(
            reading_list=reading_list,
            order__gte=new_order,
            order__lt=old_order,
        ).update(order=F("order") + 1)
    else:
        ReadingListItem.objects.filter(
            reading_list=reading_list,
            order__gt=old_order,
            order__lte=new_order,
        ).update(order=F("order") - 1)

    reading_list_item.order = new_order
    reading_list_item.save(update_fields=["order"])
    return reading_list_item
