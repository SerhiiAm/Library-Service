from django.db import models
from django.conf import settings
from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    class Meta:
        ordering = ["-borrow_date"]

    @property
    def is_active(self) -> bool:
        return self.actual_return_date is None

    def __str__(self) -> str:
        return f"{self.book.title} ({self.user.email}) - {self.borrow_date}"
