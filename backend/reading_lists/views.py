from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book
from .models import ReadingList, ReadingListItem
from .selectors import (
    get_book_by_id,
    get_reading_list_by_id,
    get_reading_list_item_by_id,
    list_reading_lists_for_user,
)
from .serializers import (
    ReadingListCreateSerializer,
    ReadingListItemCreateSerializer,
    ReadingListItemSerializer,
    ReadingListItemUpdateSerializer,
    ReadingListSerializer,
    ReadingListUpdateSerializer,
)
from .services import (
    add_book_to_reading_list,
    create_reading_list,
    delete_reading_list,
    ensure_reading_list_owner,
    remove_item_from_reading_list,
    reorder_reading_list_item,
    update_reading_list,
)


class ReadingListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ReadingListListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reading_lists = list_reading_lists_for_user(user=request.user)
        paginator = ReadingListPagination()
        paginated_reading_lists = paginator.paginate_queryset(reading_lists, request)
        serializer = ReadingListSerializer(paginated_reading_lists, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ReadingListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reading_list = create_reading_list(user=request.user, name=serializer.validated_data["name"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        output = ReadingListSerializer(reading_list)
        return Response(output.data, status=status.HTTP_201_CREATED)


class ReadingListDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        try:
            reading_list = get_reading_list_by_id(reading_list_id=pk)
        except ReadingList.DoesNotExist:
            return None, Response({"detail": "Reading list not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            ensure_reading_list_owner(user=request.user, reading_list=reading_list)
        except PermissionError as exc:
            return None, Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return reading_list, None

    def get(self, request, pk):
        reading_list, error_response = self.get_object(request, pk)
        if error_response:
            return error_response

        serializer = ReadingListSerializer(reading_list)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        reading_list, error_response = self.get_object(request, pk)
        if error_response:
            return error_response

        serializer = ReadingListUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated = update_reading_list(reading_list=reading_list, name=serializer.validated_data["name"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        output = ReadingListSerializer(updated)
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        reading_list, error_response = self.get_object(request, pk)
        if error_response:
            return error_response

        delete_reading_list(reading_list=reading_list)
        return Response({"detail": "Reading list deleted successfully."}, status=status.HTTP_200_OK)


class ReadingListItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            reading_list = get_reading_list_by_id(reading_list_id=pk)
        except ReadingList.DoesNotExist:
            return Response({"detail": "Reading list not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            ensure_reading_list_owner(user=request.user, reading_list=reading_list)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReadingListItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            book = get_book_by_id(book_id=serializer.validated_data["book_id"])
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = add_book_to_reading_list(
                reading_list=reading_list,
                book=book,
                order=serializer.validated_data.get("order"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        output = ReadingListItemSerializer(item)
        return Response(output.data, status=status.HTTP_201_CREATED)


class ReadingListItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_item(self, request, pk, item_id):
        try:
            reading_list = get_reading_list_by_id(reading_list_id=pk)
        except ReadingList.DoesNotExist:
            return None, None, Response({"detail": "Reading list not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            ensure_reading_list_owner(user=request.user, reading_list=reading_list)
        except PermissionError as exc:
            return None, None, Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        try:
            item = get_reading_list_item_by_id(reading_list=reading_list, item_id=item_id)
        except ReadingListItem.DoesNotExist:
            return None, None, Response({"detail": "Reading list item not found."}, status=status.HTTP_404_NOT_FOUND)

        return reading_list, item, None

    def patch(self, request, pk, item_id):
        _, item, error_response = self.get_item(request, pk, item_id)
        if error_response:
            return error_response

        serializer = ReadingListItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_item = reorder_reading_list_item(
                reading_list_item=item,
                new_order=serializer.validated_data["order"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        output = ReadingListItemSerializer(updated_item)
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, item_id):
        _, item, error_response = self.get_item(request, pk, item_id)
        if error_response:
            return error_response

        remove_item_from_reading_list(reading_list_item=item)
        return Response({"detail": "Book removed from reading list."}, status=status.HTTP_200_OK)
