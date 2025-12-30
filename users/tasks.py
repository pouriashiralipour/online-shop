import logging
import random
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import User, UserHistory

logger = logging.getLogger(__name__)


@shared_task
def assign_otp_task(user_id):
    try:
        user = User.objects.get(id=user_id)
        user.otp = random.randint(10000, 99999)
        user.otp_datetime_created = timezone.now()
        user.save()
        print(f"[Celery OTP] OTP for {user.mobile}: {user.otp}")
    except User.DoesNotExist:
        print(f"[Celery OTP] User with id={user_id} does not exist.")


@shared_task
def delete_old_user_history():
    """
    Delete UserHistory records older than 30 days.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    deleted_count, _ = UserHistory.objects.filter(
        datetime_visited__lt=thirty_days_ago
    ).delete()
    logger.info(f"Deleted {deleted_count} old UserHistory records on {timezone.now()}")
    return f"Deleted {deleted_count} old UserHistory records."
