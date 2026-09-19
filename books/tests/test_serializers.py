from decimal import Decimal
from django.test import TestCase

from books.models import Book
from books.serializers import BookSerializer


class BookSerializerTests(TestCase):
    """Tests for verifying the BookSerializer behavior."""

    def test_contains_expected_fields(self):
        book = Book.objects.create(
            title="Clean Architecture",
            author="Robert C. Martin",
            cover=Book.CoverChoices.HARD,
            inventory=8,
            daily_fee=Decimal("3.50"),
        )
        serializer = BookSerializer(instance=book)

        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "title", "author", "cover", "inventory", "daily_fee"},
        )

    def test_book_serialization_data_matches_object_attributes(self):
        book = Book.objects.create(
            title="Refactoring",
            author="Martin Fowler",
            cover=Book.CoverChoices.SOFT,
            inventory=4,
            daily_fee=Decimal("2.10"),
        )
        serializer = BookSerializer(instance=book)

        expected_data = {
            "id": book.id,
            "title": "Refactoring",
            "author": "Martin Fowler",
            "cover": "SOFT",
            "inventory": 4,
            "daily_fee": "2.10",
        }
        self.assertEqual(serializer.data, expected_data)
