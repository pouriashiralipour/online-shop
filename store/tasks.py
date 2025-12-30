from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_order_confirmation_email(user_email):
    send_mail(
        "سفارش شما ثبت شد!",
        "از خرید شما متشکریم.",
        "no-reply@yourdomain.com",
        [user_email],
        fail_silently=False,
    )
