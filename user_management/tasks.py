from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_password_reset_email(email, reset_link):
    """
    Task to send a password reset email notification asynchronously
    using Celery.
    """
    subject = "Password Reset Request"
    message = f"Dear user,\n\nClick the link to reset your password: {reset_link}.\n\nJob Board Team"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
