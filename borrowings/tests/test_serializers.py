from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase


from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingSerializerTests(TestCase):
    """Tests for verifying borrowing serializers validation & creation logic."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="Password123!",
        )
        self.book = Book.objects.create(
            title="Clean Architecture",
            author="Robert C. Martin",
            inventory=2,
            daily_fee=Decimal("1.50"),
        )

    def test_create_serializer_decreases_inventory(self):

        payload = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        serializer = BorrowingCreateSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
        serializer.save(user=self.user)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

    def test_create_serializer_fails_when_out_of_stock(self):

        out_of_stock_book = Book.objects.create(
            title="No Stock Book",
            author="Author",
            inventory=0,
            daily_fee=Decimal("1.00"),
        )
        payload = {
            "book": out_of_stock_book.id,
            "expected_return_date": date.today() + timedelta(days=3),
        }
        serializer = BorrowingCreateSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("book", serializer.errors)

    def test_create_serializer_fails_for_past_expected_return_date(self):

        payload = {
            "book": self.book.id,
            "expected_return_date": date.today() - timedelta(days=1),
        }
        serializer = BorrowingCreateSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("expected_return_date", serializer.errors)

    def test_return_serializer_fails_if_already_returned(self):

        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=2),
            actual_return_date=date.today(),
            book=self.book,
            user=self.user,
        )
        serializer = BorrowingReturnSerializer(instance=borrowing, data={})

        self.assertFalse(serializer.is_valid())
