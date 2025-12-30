import random
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import User
from .tasks import assign_otp_task

OTP_LIMIT_SECONDS = 60
OTP_DAILY_LIMIT = 10
OTP_BLOCK_DURATION = 60
OTP_IP_DAILY_LIMIT = 200


def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        ip = x_forwarded.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def can_request_otp(mobile: str, ip: str):
    if cache.get(f"otp_blocked:{mobile}"):
        return False, _(
            "Your account has been temporarily blocked. Please try again later."
        )

    if cache.get(f"otp_limit:{mobile}"):
        return False, _("Please wait a moment and then try again.")

    daily_count = cache.get(f"otp_daily_count:{mobile}") or 0
    if daily_count >= OTP_DAILY_LIMIT:
        cache.set(f"otp_blocked:{mobile}", "1", timeout=OTP_BLOCK_DURATION)
        return False, _("Too many requests. Your account has been temporarily blocked.")

    ip_count = cache.get(f"otp_ip_daily:{ip}") or 0
    if ip_count >= OTP_IP_DAILY_LIMIT:
        return False, _(
            "The number of requests from this IP has exceeded the allowed limit."
        )

    return True, None


def mark_otp_requested(mobile: str, ip: str):
    cache.set(f"otp_limit:{mobile}", "1", timeout=OTP_LIMIT_SECONDS)

    mobile_key = f"otp_daily_count:{mobile}"
    mobile_count = cache.get(mobile_key) or 0
    if mobile_count == 0:
        cache.set(mobile_key, 1, timeout=86400)  # expire in 1 day
    else:
        cache.incr(mobile_key)

    ip_key = f"otp_ip_daily:{ip}"
    ip_count = cache.get(ip_key) or 0
    if ip_count == 0:
        cache.set(ip_key, 1, timeout=86400)
    else:
        cache.incr(ip_key)


def get_random_otp():
    return random.randint(10000, 99999)


def assign_otp(user: User):
    assign_otp_task.delay(user.id)


def is_otp_valid(user: User):
    if not user.otp_datetime_created:
        return False
    return (timezone.now() - user.otp_datetime_created) <= timedelta(minutes=1)


def verify_otp(user: User, otp: int):
    return user.otp == otp and is_otp_valid(user)
