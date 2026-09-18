from datetime import date
from celery import shared_task
from borrowings.models import Borrowing
from notifications.telegram_bot import send_telegram_message


@shared_task
def check_overdue_borrowings() -> None:
    today = date.today()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    ).select_related("book", "user")

    if not overdue_borrowings.exists():
        send_telegram_message("No borrowings overdue today!")
        return

    for borrowing in overdue_borrowings:
        message = (
            f"⚠️ <b>OVERDUE BORROWING</b> ⚠️\n"
            f"<b>Borrowing ID:</b> {borrowing.id}\n"
            f"<b>User:</b> {borrowing.user.email}\n"
            f"<b>Book:</b> {borrowing.book.title}\n"
            f"<b>Expected Return Date:</b> {borrowing.expected_return_date}"
        )
        send_telegram_message(message)
