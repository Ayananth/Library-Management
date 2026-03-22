from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Book
from .selectors import list_books, get_book_by_id
from .serializers import BookSerializer
from .services import create_book, delete_book


class BookListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BookListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        books = list_books()
        paginator = BookListPagination()
        paginated_books = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(paginated_books, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = create_book(user=request.user, data=serializer.validated_data)
        output = BookSerializer(book)
        return Response(output.data, status=status.HTTP_201_CREATED)


class BookDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            book = get_book_by_id(book_id=pk)
        except Book.DoesNotExist:
            return Response(
                {"detail": "Book not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            book = get_book_by_id(book_id=pk)
        except Book.DoesNotExist:
            return Response(
                {"detail": "Book not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            delete_book(user=request.user, book=book)
        except PermissionError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response({"detail": "Book deleted successfully."}, status=status.HTTP_200_OK)
