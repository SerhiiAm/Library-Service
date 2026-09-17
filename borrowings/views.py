from datetime import date

from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from payments.models import Payment
from payments.stripe_utils import create_stripe_session
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
    BorrowingSerializer,
)
from notifications.telegram_bot import send_telegram_message


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)

        if is_active is not None:
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active_bool)

        return queryset

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        create_stripe_session(borrowing, self.request)
        message = (
            f"<b>New Borrowing Created!</b>\n\n"
            f"<b>User:</b> {borrowing.user.email}\n"
            f"<b>Book:</b> {borrowing.book.title}\n"
            f"<b>Borrow Date:</b> {borrowing.borrow_date}\n"
            f"<b>Expected Return:</b> {borrowing.expected_return_date}"
        )
        send_telegram_message(message)

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)

        today = date.today()

        with transaction.atomic():
            borrowing.actual_return_date = today
            borrowing.save()

            book = borrowing.book
            book.inventory += 1
            book.save()

        if today > borrowing.expected_return_date:
            extra_days = (today - borrowing.expected_return_date).days
            create_stripe_session(
                borrowing,
                request,
                payment_type=Payment.TypeChoices.FINE,
                extra_days=extra_days,
            )
        message = (
            f"<b>Book Returned!</b>\n\n"
            f"<b>User:</b> {borrowing.user.email}\n"
            f"<b>Book:</b> {borrowing.book.title}\n"
            f"<b>Actual Return Date:</b> {today}"
        )
        if today > borrowing.expected_return_date:
            message += f"\n<b>Status:</b> Overdue! Fine session created."

        send_telegram_message(message)

        return Response(
            BorrowingSerializer(borrowing).data,
            status=status.HTTP_200_OK,
        )
