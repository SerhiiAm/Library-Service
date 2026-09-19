from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from books.permissions import IsAdminOrReadOnly


class IsAdminOrReadOnlyPermissionTests(TestCase):
    """Tests for verifying custom IsAdminOrReadOnly permission."""

    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsAdminOrReadOnly()
        self.user_model = get_user_model()

        self.regular_user = self.user_model.objects.create_user(
            email="user@test.com",
            password="Password123!",
        )
        self.admin_user = self.user_model.objects.create_superuser(
            email="admin@test.com",
            password="Password123!",
        )

    def test_safe_methods_allowed_for_anonymous_user(self):
        request = self.factory.get("/")

        self.assertTrue(self.permission.has_permission(request, None))

    def test_unsafe_methods_forbidden_for_regular_user(self):
        request = self.factory.post("/")
        request.user = self.regular_user

        self.assertFalse(self.permission.has_permission(request, None))

    def test_unsafe_methods_allowed_for_admin_user(self):
        request = self.factory.post("/")
        request.user = self.admin_user

        self.assertTrue(self.permission.has_permission(request, None))
