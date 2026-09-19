import stripe
from django.conf import settings
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentSerializer
from notifications.telegram_bot import send_telegram_message

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing__user", "borrowing__book")
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        return queryset

    @action(detail=False, methods=["get"], url_path="success")
    def success(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(self.get_queryset(), session_id=session_id)

        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save()
            message = (
                f"<b>Payment Successful!</b>\n\n"
                f"<b>Payment ID:</b> {payment.id}\n"
                f"<b>User:</b> {payment.borrowing.user.email}\n"
                f"<b>Amount:</b> ${payment.money_to_pay}\n"
                f"<b>Type:</b> {payment.get_type_display()}"
            )
            send_telegram_message(message)
            return Response(
                {"message": f"Payment #{payment.id} successful!"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Payment has not been completed yet."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], url_path="cancel")
    def cancel(self, request):
        return Response(
            {"message": "Payment paused. You can complete it within 24 hours."},
            status=status.HTTP_200_OK,
        )
