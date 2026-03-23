import logging

from django.db import transaction
from django.db.models import F, Max

from .models import ReadingList, ReadingListItem

logger = logging.getLogger(__name__)


def create_reading_list(*, user, name):
    if ReadingList.objects.filter(user=user, name=name).exists():
        logger.warning(
            "Reading list create rejected (duplicate name): user_id=%s name=%s",
            user.id,
            name,
        )
        raise ValueError("You already have a reading list with this name.")
    reading_list = ReadingList.objects.create(user=user, name=name)
    logger.info(
        "Reading list created: reading_list_id=%s user_id=%s",
        reading_list.id,
        user.id,
    )
    return reading_list


def update_reading_list(*, reading_list, name):
    if (
        ReadingList.objects.filter(user=reading_list.user, name=name)
        .exclude(pk=reading_list.pk)
        .exists()
    ):
        logger.warning(
            "Reading list update rejected (duplicate name): reading_list_id=%s user_id=%s name=%s",
            reading_list.id,
            reading_list.user_id,
            name,
        )
        raise ValueError("You already have a reading list with this name.")
    previous_name = reading_list.name
    reading_list.name = name
    reading_list.save(update_fields=["name"])
    logger.info(
        "Reading list renamed: reading_list_id=%s user_id=%s old_name=%s new_name=%s",
        reading_list.id,
        reading_list.user_id,
        previous_name,
        name,
    )
    return reading_list


def delete_reading_list(*, reading_list):
    reading_list_id = reading_list.id
    user_id = reading_list.user_id
    reading_list.delete()
    logger.info(
        "Reading list deleted: reading_list_id=%s user_id=%s",
        reading_list_id,
        user_id,
    )


def ensure_reading_list_owner(*, user, reading_list):
    if reading_list.user_id != user.id:
        logger.warning(
            "Reading list access denied: reading_list_id=%s owner_id=%s actor_id=%s",
            reading_list.id,
            reading_list.user_id,
            user.id,
        )
        raise PermissionError("You cannot access this reading list.")


@transaction.atomic
def add_book_to_reading_list(*, reading_list, book, order=None):
    if ReadingListItem.objects.filter(reading_list=reading_list, book=book).exists():
        logger.warning(
            "Reading list add rejected (duplicate book): reading_list_id=%s book_id=%s",
            reading_list.id,
            book.id,
        )
        raise ValueError("This book already exists in the reading list.")

    max_order = (
        ReadingListItem.objects.filter(reading_list=reading_list).aggregate(max_order=Max("order"))["max_order"]
        or 0
    )

    if order is None:
        target_order = max_order + 1
    else:
        if order < 1:
            logger.warning(
                "Reading list add rejected (invalid order): reading_list_id=%s order=%s",
                reading_list.id,
                order,
            )
            raise ValueError("Order must be 1 or higher.")

        if order > max_order + 1:
            logger.warning(
                "Reading list add rejected (order too high): reading_list_id=%s requested_order=%s max_allowed=%s",
                reading_list.id,
                order,
                max_order + 1,
            )
            raise ValueError(f"Order cannot be greater than {max_order + 1}.")

        ReadingListItem.objects.filter(reading_list=reading_list, order__gte=order).update(
            order=F("order") + 1
        )
        target_order = order

    item = ReadingListItem.objects.create(
        reading_list=reading_list,
        book=book,
        order=target_order,
    )
    logger.info(
        "Book added to reading list: item_id=%s reading_list_id=%s book_id=%s order=%s",
        item.id,
        reading_list.id,
        book.id,
        target_order,
    )
    return item


@transaction.atomic
def remove_item_from_reading_list(*, reading_list_item):
    reading_list = reading_list_item.reading_list
    reading_list_item_id = reading_list_item.id
    book_id = reading_list_item.book_id
    removed_order = reading_list_item.order

    reading_list_item.delete()

    ReadingListItem.objects.filter(reading_list=reading_list, order__gt=removed_order).update(
        order=F("order") - 1
    )
    logger.info(
        "Reading list item removed: item_id=%s reading_list_id=%s book_id=%s removed_order=%s",
        reading_list_item_id,
        reading_list.id,
        book_id,
        removed_order,
    )


@transaction.atomic
def reorder_reading_list_item(*, reading_list_item, new_order):
    reading_list = reading_list_item.reading_list
    old_order = reading_list_item.order

    total_items = ReadingListItem.objects.filter(reading_list=reading_list).count()
    if new_order < 1 or new_order > total_items:
        logger.warning(
            "Reading list reorder rejected (invalid order): item_id=%s reading_list_id=%s requested_order=%s total_items=%s",
            reading_list_item.id,
            reading_list.id,
            new_order,
            total_items,
        )
        raise ValueError(f"Order must be between 1 and {total_items}.")

    if new_order == old_order:
        logger.info(
            "Reading list reorder skipped (same order): item_id=%s reading_list_id=%s order=%s",
            reading_list_item.id,
            reading_list.id,
            old_order,
        )
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
    logger.info(
        "Reading list item reordered: item_id=%s reading_list_id=%s old_order=%s new_order=%s",
        reading_list_item.id,
        reading_list.id,
        old_order,
        new_order,
    )
    return reading_list_item
