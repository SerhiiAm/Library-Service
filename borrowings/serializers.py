from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError
from borrowings.models import Borrowing
from datetime import date


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")

    def validate(self, attrs):
        data = super().validate(attrs)
        book = attrs["book"]

        if book.inventory <= 0:
            raise ValidationError({"book": "This book is currently out of stock."})

        if attrs["expected_return_date"] < date.today():
            raise ValidationError(
                {"expected_return_date": "Expected return date cannot be in the past."}
            )

        return data

    def create(self, validated_data):

        with transaction.atomic():
            book = validated_data["book"]
            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(**validated_data)
            return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ()

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise ValidationError("This borrowing has already been returned.")
        return attrs
