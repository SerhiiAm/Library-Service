from decimal import Decimal
from django.test import TestCase

from books.models import Book


class BookModelTests(TestCase):
    """Tests for verifying the Book model."""

    def test_book_str(self):

        book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover=Book.CoverChoices.HARD,
            inventory=10,
            daily_fee=Decimal("1.99"),
        )


        self.assertEqual(str(book), "Clean Code - Robert C. Martin")

    def test_book_creation_with_default_cover(self):

        book = Book.objects.create(
            title="Refactoring",
            author="Martin Fowler",
            inventory=5,
            daily_fee=Decimal("2.50"),
        )


        self.assertEqual(book.cover, Book.CoverChoices.HARD)
        self.assertEqual(book.inventory, 5)
        self.assertEqual(book.daily_fee, Decimal("2.50"))
