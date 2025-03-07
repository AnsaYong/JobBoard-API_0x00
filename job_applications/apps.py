from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError


def create_default_statuses(sender, **kwargs):
    """
    Create default job application statuses after migrations.
    """
    from job_applications.models import JobApplicationStatus  # Aavoids circular imports

    default_statuses = [
        {
            "job_status_code": "Pending",
            "description": "Application received and awaiting review",
        },
        {
            "job_status_code": "Under Review",
            "description": "Application is being reviewed by the employer",
        },
        {
            "job_status_code": "Interview Scheduled",
            "description": "Employer has scheduled an interview",
        },
        {"job_status_code": "Hired", "description": "Candidate has been hired"},
        {"job_status_code": "Rejected", "description": "Candidate has been rejected"},
    ]

    try:
        for status in default_statuses:
            JobApplicationStatus.objects.get_or_create(
                job_status_code=status["job_status_code"], defaults=status
            )
    except (OperationalError, ProgrammingError):
        # Ignore errors if the database is not ready yet (e.g., first migration)
        pass


class JobApplicationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "job_applications"

    def ready(self):
        post_migrate.connect(create_default_statuses, sender=self)
        import job_applications.signals
