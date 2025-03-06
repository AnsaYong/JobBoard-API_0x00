import uuid
from django.db import models
from django.contrib.auth import get_user_model
from job_listings.models import JobPosting

User = get_user_model()


class JobApplicationStatus(models.Model):
    """
    Model to store the status of a job application.

    Each job application has a status associated with it,
    such as "Pending", "Accepted", or "Rejected".
    This model is used to define all possible statuses for job applications.

    Attributes:
        - `status_id` (UUIDField): The unique identifier for the status.
        - `status_code` (CharField): A unique code representing the status
        (e.g., "Pending", "Accepted").
        - `description` (CharField): A textual description of the status
        (e.g., "Application is currently under review").
    """

    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Job Application Statuses"
        ordering = ["status_code"]

    def __str__(self):
        """Return the status code as the string representation of the object."""
        return self.status_code


class JobApplication(models.Model):
    """
    Model to store the job applications.

    This model represents a job application submitted by a job seeker for a particular job posting.
    The application includes information about the job seeker, resume, cover letter, status, and timestamps.

    Attributes:
        - `application_id` (UUIDField): The unique identifier for the application.
        - `job` (ForeignKey): The job posting to which the application is submitted.
        - `job_seeker` (ForeignKey): The job seeker who submitted the application.
        - `resume_url` (TextField): The URL to the job seeker's resume.
        - `cover_letter_url` (TextField): The URL to the job seeker's cover letter.
        - `status` (ForeignKey): The status of the application (e.g., "Pending", "Accepted").
        - `applied_at` (DateTimeField): The timestamp when the application was submitted.
        - `updated_at` (DateTimeField): The timestamp when the application was last updated.
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

        If the application does not already have a status assigned, the status
        will be set to "Pending". This ensures that every new application has
        an initial status by default.
        """
        if not self.status:
            pending_status = JobApplicationStatus.objects.filter(
                status_code="Pending"
            ).first()
            if pending_status:
                self.status = pending_status
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the job title and jobseeker's name as a string representation."""
        return f"{self.job.title} - {self.job_seeker.first_name}"


class JobApplicationStatusHistory(models.Model):
    """
    Model to store the history of status changes of a job application.

    This model tracks the history of status changes for each job application,
    allowing for a historical record of status transitions.

    Attributes:
        - `status_hist_id` (UUIDField): The unique identifier for the status history entry.
        - `job_application` (ForeignKey): The job application associated with the status change.
        - `status` (ForeignKey): The new status of the job application.
        - `changed_at` (DateTimeField): The timestamp when the status was changed.
        - `changed_by` (ForeignKey): The user who changed the status.
    """

    status_hist_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    job_application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.ForeignKey(JobApplicationStatus, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Job Application Status History"
        ordering = ["-changed_at"]

    def __str__(self):
        """
        Return the job title, status code and date status was changed as a
        string representation of the status change history entry.
        """
        return f"{self.job_application.job.title} - {self.status.status_code} at {self.changed_at}"
