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

    class Meta:
        verbose_name_plural = "Job Application Statuses"
        ordering = ["status_code"]

    def __str__(self):
        return self.status_code


class JobApplication(models.Model):
    """
    Model to store the job applications
    """

    application_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    job = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="applications"
    )
    job_seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    resume_url = models.TextField()
    cover_letter_url = models.TextField()
    status = models.ForeignKey(
        JobApplicationStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Job Applications"
        indexes = [
            models.Index(fields=["job", "job_seeker"]),
        ]
        ordering = ["-applied_at"]

    def save(self, *args, **kwargs):
        """
        Assign a default status ('Pending') when a new application is created.
        """
        if not self.status:
            pending_status = JobApplicationStatus.objects.filter(
                status_code="Pending"
            ).first()
            if pending_status:
                self.status = pending_status
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job.title} - {self.job_seeker.username}"


class JobApplicationStatusHistory(models.Model):
    """
    Model to store the history of status changes of a job application
    """

    status_hist_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    job_application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.ForeignKey(JobApplicationStatus, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Employer or Admin who changes the status

    class Meta:
        verbose_name_plural = "Job Application Status History"

    def __str__(self):
        return f"{self.job_application.job.title} - {self.status.status_code} at {self.changed_at}"
