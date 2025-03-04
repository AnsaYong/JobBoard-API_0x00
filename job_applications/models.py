import uuid
from django.db import models
from django.contrib.auth import get_user_model
from job_listings.models import JobPosting

User = get_user_model()


class JobApplicationStatus(models.Model):
    """
    Model to store the status of a job application
    """

    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.status_code


class JobApplication(models.Model):
    """
    Model to store the job applications
    """

    job_application_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    job_id = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="applications"
    )
    job_seeker_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    resume_url = models.TextField()
    cover_letter_url = models.TextField()
    status = models.ForeignKey(
        JobApplicationStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["job", "job_seeker"]),
        ]

    def __str__(self):
        return f"{self.job.title} - {self.job_seeker.username}"


class JobApplicationStatusHistory(models.Model):
    """
    Model to store the history of status changes of a job application
    """

    status_hist_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    job_application_id = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.ForeignKey(JobApplicationStatus, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Employer or Admin who changes the status

    def __str__(self):
        return f"{self.job_application.job.title} - {self.status.status_code} at {self.changed_at}"
