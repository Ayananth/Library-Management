from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]

    def validate_publication_date(self, value):
        from datetime import date

        if value > date.today():
            raise serializers.ValidationError("Publication date cannot be in the future.")
        return value
