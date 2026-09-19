from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

PAYMENTS_URL = reverse("payments:payment-list")
SUCCESS_URL = reverse("payments:payment-success")
CANCEL_URL = reverse("payments:payment-cancel")


class PaymentViewSetTests(TestCase):
    """Tests for PaymentViewSet endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="Password123!",
        )
        self.other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="Password123!",
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=5,
            daily_fee=Decimal("2.00"),
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=2),
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/test",
            session_id="sess_test_123",
            money_to_pay=Decimal("4.00"),
        )
        self.client.force_authenticate(self.user)

    def test_unauthenticated_user_access_denied(self):
        self.client.logout()
        response = self.client.get(PAYMENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_see_only_own_payments(self):
        other_borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=2),
            book=self.book,
            user=self.other_user,
        )
        Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=other_borrowing,
            money_to_pay=Decimal("4.00"),
        )

        response = self.client.get(PAYMENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.payment.id)

    def test_success_missing_session_id_returns_400(self):
        response = self.client.get(SUCCESS_URL)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("payments.views.send_telegram_message")
    @patch("payments.views.stripe.checkout.Session.retrieve")
    def test_success_paid_session_updates_status(
            self, mock_stripe_retrieve, mock_telegram
    ):
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_stripe_retrieve.return_value = mock_session

        response = self.client.get(
            f"{SUCCESS_URL}?session_id={self.payment.session_id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PAID)
        mock_telegram.assert_called_once()

    def test_cancel_endpoint_returns_200(self):
        response = self.client.get(CANCEL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
