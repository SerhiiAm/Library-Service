from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing


class BorrowingModelTests(TestCase):
    """Tests for verifying the Borrowing model behavior."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="Password123!",
        )
        self.book = Book.objects.create(
            title="Design Patterns",
            author="Erich Gamma",
            inventory=3,
            daily_fee=Decimal("2.00"),
        )

    def test_borrowing_str(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=5),
            book=self.book,
            user=self.user,
        )

        expected_str = (
            f"{self.book.title} ({self.user.email}) - {borrowing.borrow_date}"
        )
        self.assertEqual(str(borrowing), expected_str)

    def test_is_active_property_when_not_returned(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=5),
            book=self.book,
            user=self.user,
        )

        self.assertTrue(borrowing.is_active)

    def test_is_active_property_when_returned(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=5),
            actual_return_date=date.today(),
            book=self.book,
            user=self.user,
        )

        self.assertFalse(borrowing.is_active)
