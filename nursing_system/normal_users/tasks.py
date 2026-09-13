from celery import shared_task
from datetime import timedelta
from django.utils.timezone import now
from .models import OtpCodeModel

@shared_task
def cleanup_expired_otps():
    """
    A Celery task to delete expired OTP codes from the database.
    Expired OTPs are those older than the expiration time defined in the model.
    """
    expiration_time = timedelta(minutes=3)
    expired_otps = OtpCodeModel.objects.filter(created__lt=now() - expiration_time)
    count = expired_otps.count()  # Count how many are being deleted for logging/debugging
    expired_otps.delete()
    return f"{count} expired OTPs deleted."


# otp/tasks.py
import os
import requests
from django.conf import settings

# Reuse a single Session in this worker process
session = requests.Session()
session.headers.update({'Content-Type': 'application/json'})

@shared_task(bind=True, time_limit=10)
def send_otp_sms(self, phone_number: str, code: str):
    """
    Celery task to send OTP SMS via otp terminal (no retries).
    - If requests.post raises a RequestException, we re‐raise it so Celery
      marks the task as failed immediately.
    - time_limit=10 ensures Celery kills the task if it hangs >10s.
    """

    try:
        pass
        print(code)
    except Exception:
        raise Exception("خطا در ارسال کد")
