from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_application_status_notification(email, job_title, new_status):
    """
    Task to send an email notification when the status of a job application changes.
    """
    subject = f"Update on Your Job Application for {job_title}"
    message = f"Dear applicant,\n\nYour job application status has been updated to: {new_status}.\n\nBest regards,\nJob Board Team"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
