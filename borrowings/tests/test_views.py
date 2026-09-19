from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id: int) -> str:
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id: int) -> str:
    return reverse("borrowings:borrowing-return-borrowing", args=[borrowing_id])


class BorrowingViewSetTests(TestCase):
    """Tests for BorrowingViewSet endpoints."""

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
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="Password123!",
        )
        self.book = Book.objects.create(
            title="Refactoring",
            author="Martin Fowler",
            inventory=5,
            daily_fee=Decimal("2.50"),
        )
        self.client.force_authenticate(self.user)

    def test_unauthenticated_user_access_denied(self):
        self.client.logout()
        response = self.client.get(BORROWINGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_see_own_borrowings(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=3),
            book=self.book,
            user=self.user,
        )
        Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=3),
            book=self.book,
            user=self.other_user,
        )

        response = self.client.get(BORROWINGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], borrowing1.id)

    @patch("borrowings.views.send_telegram_message")
    @patch("borrowings.views.create_stripe_session")
    def test_create_borrowing_successful(self, mock_stripe, mock_telegram):
        payload = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=5),
        }
        response = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_stripe.assert_called_once()
        mock_telegram.assert_called_once()

    @patch("borrowings.views.send_telegram_message")
    def test_return_borrowing_increases_inventory(self, mock_telegram):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=3),
            book=self.book,
            user=self.user,
        )
        initial_inventory = self.book.inventory
        url = return_url(borrowing.id)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.book.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, initial_inventory + 1)
        mock_telegram.assert_called_once()
