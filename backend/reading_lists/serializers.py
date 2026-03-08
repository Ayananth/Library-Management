from rest_framework import serializers

from books.models import Book
from .models import ReadingList, ReadingListItem


class BookSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "authors", "genre", "publication_date"]


class ReadingListItemSerializer(serializers.ModelSerializer):
    book = BookSummarySerializer(read_only=True)

    class Meta:
        model = ReadingListItem
        fields = ["id", "order", "book"]


class ReadingListSerializer(serializers.ModelSerializer):
    items = ReadingListItemSerializer(many=True, read_only=True)

    class Meta:
        model = ReadingList
        fields = ["id", "name", "created_at", "items"]


class ReadingListCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class ReadingListUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class ReadingListItemCreateSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(min_value=1)
    order = serializers.IntegerField(min_value=1, required=False)


class ReadingListItemUpdateSerializer(serializers.Serializer):
    order = serializers.IntegerField(min_value=1)
