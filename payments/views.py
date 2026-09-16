import stripe
from django.conf import settings
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentSerializer

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
            return Response({"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(self.get_queryset(), session_id=session_id)
        if not payment:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save()
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
