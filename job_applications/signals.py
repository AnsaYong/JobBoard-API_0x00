from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JobApplication
from .tasks import send_application_status_notification


@receiver(post_save, sender=JobApplication)
def job_application_status_update(sender, instance, created, **kwargs):
    """
    Signal receiver to send an email notification when the status
    of a job application changes.
    """
    if not created:
        job_seeker_email = instance.job_seeker.email
        job_title = instance.job.title
        new_status = instance.get_status_display()

        # Trigger the Celery task to send the email notification
        send_application_status_notification.delay(
            job_seeker_email, job_title, new_status
        )
