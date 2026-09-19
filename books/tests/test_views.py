from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id: int) -> str:
    return reverse("books:book-detail", args=[book_id])


def sample_book(**params) -> Book:
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": Book.CoverChoices.HARD,
        "inventory": 5,
        "daily_fee": Decimal("1.50"),
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBooksApiTests(TestCase):
    """Tests for unauthenticated / read-only users in BookViewSet."""

    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        sample_book()
        sample_book(title="Another Book")

        response = self.client.get(BOOKS_URL)
        books = Book.objects.all().order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )
        self.assertEqual(results, serializer.data)

    def test_get_book_detail(self):
        book = sample_book()
        url = detail_url(book.id)

        response = self.client.get(url)
        serializer = BookSerializer(book)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_unauthorized_forbidden(self):
        payload = {
            "title": "Unauthorized Book",
            "author": "Anon",
            "cover": Book.CoverChoices.HARD,
            "inventory": 2,
            "daily_fee": "2.00",
        }
        response = self.client.post(BOOKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminBooksApiTests(TestCase):
    """Tests for admin users with full access permissions in BookViewSet."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="Password123!",
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_book_successful(self):

        payload = {
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "cover": Book.CoverChoices.HARD,
            "inventory": 10,
            "daily_fee": "2.99",
        }
        response = self.client.post(BOOKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=response.data["id"])
        for key in payload:
            if key == "daily_fee":
                self.assertEqual(Decimal(payload[key]), getattr(book, key))
            else:
                self.assertEqual(payload[key], getattr(book, key))

    def test_update_book(self):

        book = sample_book()
        payload = {"title": "Updated Title", "inventory": 15}
        url = detail_url(book.id)

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.inventory, payload["inventory"])

    def test_delete_book(self):

        book = sample_book()
        url = detail_url(book.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
