from rest_framework import serializers
from django.contrib.auth import get_user_model
from job_listings.models import JobPosting
from .models import JobApplication, JobApplicationStatus, JobApplicationStatusHistory

User = get_user_model()


class JobApplicationStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobApplicationStatus model.

    This serializer represents the status of a job application. It includes:
    - `status_id`: The unique identifier for the status.
    - `job_status_code`: A short code (such as "Pending", "Accepted", etc.) representing the status.
    - `description`: A detailed explanation or description of the status.

    Used to fetch or serialize details of the job application status in the API responses.
    """

    class Meta:
        model = JobApplicationStatus
        fields = ["status_id", "job_status_code", "description"]


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobApplication model.

    This serializer is used to represent a job application, including the job posting,
    job seeker, resume and cover letter URLs, the application status, and relevant timestamps.

    - `job`: The job related to this application (represented by a PrimaryKey).
    - `job_seeker`: The user who applied for the job (represented by a PrimaryKey).
    - `status`: The current status of the job application (represented by a nested JobApplicationStatus).
    - `resume_url`: The URL to the resume submitted by the job seeker.
    - `cover_letter_url`: The URL to the cover letter submitted by the job seeker.
    - `applied_at`: The timestamp when the application was submitted (read-only).
    - `updated_at`: The timestamp when the application was last updated (read-only).

    This serializer is used to serialize job application data, either for listing job applications
    or for fetching details about a specific application.
    """

    job = serializers.PrimaryKeyRelatedField(read_only=True)
    job_seeker = serializers.PrimaryKeyRelatedField(read_only=True)
    status = JobApplicationStatusSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "application_id",
            "job",
            "job_seeker",
            "resume_url",
            "cover_letter_url",
            "status",
            "applied_at",
            "updated_at",
        ]
        read_only_fields = ["application_id", "applied_at", "updated_at"]


class JobApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the JobApplicationStatusHistory model.

    This serializer is used to represent the history of status changes for a job application.

    - `status_hist_id`: The unique identifier for the status change record.
    - `job_application`: The related job application for which the status change occurred.
    - `status`: The status that was applied to the job application (represented by a nested JobApplicationStatus).
    - `changed_at`: The timestamp when the status change occurred.
    - `changed_by`: The user who changed the status (represented by a StringRelatedField).

    This serializer is used to fetch or serialize the status history of a particular job application.
    It provides insights into when and by whom the job application status was modified.
    """

    status = JobApplicationStatusSerializer()
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = JobApplicationStatusHistory
        fields = [
            "status_hist_id",
            "job_application",
            "status",
            "changed_at",
            "changed_by",
        ]
