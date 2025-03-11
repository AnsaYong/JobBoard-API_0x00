from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from job_listings.models import JobPosting
from .models import JobApplication, JobApplicationStatus, JobApplicationStatusHistory
from .serializers import (
    JobApplicationSerializer,
    JobApplicationStatusSerializer,
    JobApplicationStatusHistorySerializer,
)
from permissions import IsJobBoardAdmin, IsEmployer, IsJobseeker


class JobApplicationStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing the job application statuses.

    This endpoint provides access to the different statuses
    a job application can have, such as:
    - "Pending"
    - "Under Review"
    - "Interview Scheduled"
    - "Hired"
    - "Rejected"

    ## Example Request:
    **GET api/statuses/**
    Example response:
    ```json
    [
        {
            "status_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "job_status_code": "Pending",
            "description": "Application received and awaiting review"
        },
        {
            "status_id": "a47ac10b-58cc-4372-b567-1e02b2c3d479",
            "job_status_code": "Hired",
            "description": "Candidate has been hired"
        }
    ]
    ```

    ## Fields:
    - `status_id`: The unique identifier for the status.
    - `job_status_code`: A short code (e.g., "Under Review", "Hired") representing the application status.
    - `description`: A detailed explanation or description of the status.
    """

    queryset = JobApplicationStatus.objects.all()
    serializer_class = JobApplicationStatusSerializer


class ApplicationStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving the current status of a job application.

    This endpoint is specific to a job application and allows retrieving
    or updating the status for that application.

    ## Example Request:
    **GET /applications/12345678-abcd-1234-abcd-1234abcd5678/status/**
    Example response:
    ```json
    {
        "status_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "job_status_code": "Pending",
        "description": "The application is currently under review."
    }
    ```

    ## Example Request:
    **POST /applications/12345678-abcd-1234-abcd-1234abcd5678/status/update/**
    Request payload:
    ```json
    {
        "job_status_code": "Hired"
    }
    ```
    Example response:
    ```json
    {
        "message": "Status updated successfully",
        "new_status": "Accepted"
    }
    ```

    ## Fields:
    - `job_status_code`: The new status code to update the job application
    (e.g., "Hired", "Rejected").
    """

    queryset = JobApplicationStatus.objects.all()
    serializer_class = JobApplicationStatusSerializer

    def get_queryset(self):
        """
        Filtering the status based on the job application id provided
        in the URL path.

        **GET /applications/{application_id}/status/** will return the
        status of a specific application.
        """
        queryset = super().get_queryset()

        application_id = self.kwargs.get("application_pk")
        if application_id:
            application = get_object_or_404(
                JobApplication, application_id=application_id
            )
            return queryset.filter(status_id=application.status.status_id)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Job Applications.

    This endpoint allows job seekers to apply for jobs, and employers
    to view, filter, and update applications.


    ## Example Request:
    **GET /jobs/1234/applications/**
    Example response:
    ```json
    [
        {
            "application_id": "1bfc5d19-e3f5-4b8f-b6f7-4106b25107a5",
            "job": 1234,
            "job_seeker": 5678,
            "resume_url": "http://example.com/resume.pdf",
            "cover_letter_url": "http://example.com/cover_letter.pdf",
            "status": {
                "job_status_code": "Pending",
                "description": "The application is currently under review."
            },
            "applied_at": "2025-03-01T12:00:00Z",
            "updated_at": "2025-03-02T14:00:00Z"
        }
    ]
    ```

    ## Example Request:
    **POST /jobs/1234/applications/**
    Request payload:
    ```json
    {
        "resume_url": "http://example.com/resume.pdf",
        "cover_letter_url": "http://example.com/cover_letter.pdf"
    }
    ```
    Example response:
    ```json
    {
        "application_id": "1bfc5d19-e3f5-4b8f-b6f7-4106b25107a5",
        "job": 1234,
        "job_seeker": 5678,
        "resume_url": "http://example.com/resume.pdf",
        "cover_letter_url": "http://example.com/cover_letter.pdf",
        "status": {
            "job_status_code": "Pending",
            "description": "The application is currently under review."
        },
        "applied_at": "2025-03-01T12:00:00Z",
        "updated_at": "2025-03-02T14:00:00Z"
    }
    ```

    ## Example Request:
    **POST /jobs/1234/applications/1bfc5d19-e3f5-4b8f-b6f7-4106b25107a5/update-status/**
    Request payload:
    ```json
    {
        "job_status_code": "Hired"
    }
    ```
    Example response:
    ```json
    {
        "message": "Status updated successfully",
        "new_status": "Hired"
    }
    ```
    """

    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        """
        Filters job applications based on user role (job seeker or employer).

        - Superusers can view all applications.
        - Admins can view applications for jobs they are the employer of.
        - Job seekers can view only their own applications.

        Filters can also be applied by job ID when available in the URL path.

        **GET /jobs/{job_pk}/applications/** will return job applications for a specific job.
        """
        if getattr(self, "swagger_fake_view", False):
            return JobApplication.objects.none()

        queryset = super().get_queryset()
        user = self.request.user
        job_id = self.kwargs.get("job_pk")
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        if user.is_superuser:
            return queryset

        if user.role == "admin":
            return queryset.filter(job__employer=user)

        return queryset.filter(job_seeker=user)

    def perform_create(self, serializer):
        """
        Ensures the job exists, the user is not applying to their own job,
        and the application is properly associated with the job.

        **POST /jobs/{job_pk}/applications/**: Creates a new job application
        for the given job, submitted by the job seeker.
        """
        user = self.request.user
        job_id = self.kwargs.get("job_pk")

        job = get_object_or_404(JobPosting, job_id=job_id)

        if job.employer == user:
            raise PermissionDenied("Employer cannot apply to their own job listing.")

        serializer.save(job=job, job_seeker=user)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, job_pk=None, pk=None):
        """
        Employers can update the status of a job application.

        **POST api/jobs/{job_pk}/applications/{application_id}/update-status/**: Allows the
        employer to change the application status (e.g., from "Pending" to "Accepted").

        ## Required Payload:
        - `job_status_code`: The new status to apply to the job application.
        The available statuses can be viewd at `/api/statuses/`.
        (e.g., "Hired", "Rejected", "Interview Scheduled").

        **403 Forbidden**: If the request is not made by the employer associated with the job.

        ## Response:
        - `message`: Confirmation of the status update.
        - `new_status`: The new status code applied.
        """
        job_application = get_object_or_404(JobApplication, application_id=pk)

        # Ensure only the employer can update the status
        if job_application.job.employer != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        job_status_code = request.data.get("status_code")
        status = get_object_or_404(JobApplicationStatus, status_code=job_status_code)

        # Log status change history
        JobApplicationStatusHistory.objects.create(
            job_application=job_application, status=status, changed_by=request.user
        )

        # Update application status
        job_application.status = status
        job_application.save()

        return Response(
            {"message": "Status updated successfully", "new_status": job_status_code}
        )


class JobApplicationStatusHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing the history of status changes for a job application.

    **GET /applications/{application_id}/status-history/**: Retrieve the
    history of status changes for a specific job application.

    This endpoint provides a list of all status changes, including the status
    code, the timestamp of when the status was changed, and who changed it.

    ## Example Request:
    **GET /applications/12345678-abcd-1234-abcd-1234abcd5678/status-history/**
    Example response:
    ```json
    [
        {
            "status_hist_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "status": {
                "job_status_code": "Pending",
                "description": "The application is currently under review."
            },
            "changed_at": "2025-03-01T12:00:00Z",
            "changed_by": "employer_username"
        },
        {
            "status_hist_id": "a47ac10b-58cc-4372-b567-1e02b2c3d479",
            "status": {
                "job_status_code": "Accepted",
                "description": "The application has been accepted."
            },
            "changed_at": "2025-03-02T14:00:00Z",
            "changed_by": "employer_username"
        }
    ]
    ```

    ## Fields:
    - `status_hist_id`: The unique identifier for the status history record.
    - `status`: The status that was applied (represented by a nested `JobApplicationStatus`).
    - `changed_at`: Timestamp of when the status was changed.
    - `changed_by`: The user who changed the status (represented by their username).
    """

    queryset = JobApplicationStatusHistory.objects.all()
    serializer_class = JobApplicationStatusHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns the status history for a specific job application, identified
        by the `application_id` provided in the URL path.

        **GET /applications/{application_id}/status-history/** will return the
        status change history for the application.
        """
        queryset = super().get_queryset()

        application_id = self.kwargs.get("application_pk")
        if application_id:
            return queryset.filter(job_application_id=application_id)
