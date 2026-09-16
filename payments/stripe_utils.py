import stripe
from django.conf import settings
from django.urls import reverse
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing, request, payment_type=Payment.TypeChoices.PAYMENT, extra_days=0):
    if payment_type == Payment.TypeChoices.PAYMENT:
        days = (borrowing.expected_return_date - borrowing.borrow_date).days or 1
        price = borrowing.book.daily_fee * days
    else:

        multiplier = getattr(settings, "FINE_MULTIPLIER", 2)
        price = borrowing.book.daily_fee * extra_days * multiplier

    unit_amount = int(price * 100)

    success_url = request.build_absolute_uri(reverse("payments:payment-success")) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payments:payment-cancel")) + "?session_id={CHECKOUT_SESSION_ID}"

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{payment_type} for {borrowing.book.title}",
                    },
                    "unit_amount": unit_amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=payment_type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=price,
    )
    return payment
