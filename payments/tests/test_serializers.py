from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentSerializer


class PaymentSerializerTests(TestCase):
    """Tests for verifying Payment serializers."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="Password123!",
        )
        self.book = Book.objects.create(
            title="Clean Architecture",
            author="Robert C. Martin",
            inventory=3,
            daily_fee=Decimal("1.50"),
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=3),
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/test",
            session_id="sess_12345",
            money_to_pay=Decimal("4.50"),
        )

    def test_payment_detail_serializer_fields(self):
        serializer = PaymentSerializer(instance=self.payment)
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "status",
                "type",
                "borrowing",
                "session_url",
                "session_id",
                "money_to_pay",
            },
        )
        self.assertEqual(data["session_id"], "sess_12345")

    def test_payment_list_serializer_fields(self):
        serializer = PaymentListSerializer(instance=self.payment)
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            {"id", "status", "type", "money_to_pay"},
        )
