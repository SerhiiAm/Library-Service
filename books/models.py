from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD", "Hardcover"
        SOFT = "SOFT", "Paperback"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4,
        choices=CoverChoices.choices,
        default=CoverChoices.HARD,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.title} - {self.author}"
