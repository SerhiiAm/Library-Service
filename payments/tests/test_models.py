from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class PaymentModelTests(TestCase):
    """Tests for verifying the Payment model functionality."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="Password123!",
        )
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            inventory=5,
            daily_fee=Decimal("2.00"),
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=5),
            book=self.book,
            user=self.user,
        )

    def test_payment_str(self):
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            money_to_pay=Decimal("10.00"),
        )

        expected_str = "PAYMENT (PENDING) - $10.00"
        self.assertEqual(str(payment), expected_str)
