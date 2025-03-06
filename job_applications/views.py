from django.shortcuts import get_object_or_404
from rest_framework import viewsets
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
    serializer_class = JobApplicationStatusSerializer

    def get_queryset(self):
        """
        Filtering status based on the job application id
        """
        application = get_object_or_404(
            JobApplication, application_id=self.kwargs["application_id"]
        )
        return JobApplicationStatus.objects.filter(
            status_id=application.status.status_id
        )


class JobApplicationViewSet(viewsets.ModelViewSet):

    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        """
        Allows filtering of applications based on user role (job seeker or employer)
        """
        user = self.request.user
        job_id = self.kwargs.get("job_pk")
        if job_id:
            queryset = JobApplication.objects.filter(job_id=job_id)

        if user.is_superuser:
            return queryset

        if user.role == "admin":
            return queryset.filter(job__employer=user)

        return queryset.filter(job_seeker=user)

    def perform_create(self, serializer):
        """
        Ensure the job exists, the user isn't applying to their own job,
        and correctly associate the application with the job.
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
        Employer can update the status of a job application.
        """
        job_application = get_object_or_404(JobApplication, application_id=pk)

        # Ensure only the employer can update the status
        if job_application.job.employer != request.user:
            return Response(
                {"error": "Only the employer can update the application status."},
                status=403,
            )

        status_code = request.data.get("status_code")
        status = get_object_or_404(JobApplicationStatus, status_code=status_code)

        # Log status change history
        JobApplicationStatusHistory.objects.create(
            job_application=job_application, status=status, changed_by=request.user
        )

        # Update application status
        job_application.status = status
        job_application.save()

        return Response(
            {"message": "Status updated successfully", "new_status": status_code}
        )


class JobApplicationStatusHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationStatusHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the status history for a specific job application.
        """
        application_id = self.kwargs["application_id"]
        return JobApplicationStatusHistory.objects.filter(
            job_application_id=application_id
        )
