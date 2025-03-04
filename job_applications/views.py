from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import JobApplication, JobApplicationStatus, JobApplicationStatusHistory
from .serializers import (
    JobApplicationSerializer,
    JobApplicationStatusSerializer,
    JobApplicationStatusHistorySerializer,
)
from permissions import IsJobBoardAdmin, IsEmployer, IsJobseeker


class JobApplicationStatusViewSet(viewsets.ModelViewSet):
    queryset = JobApplicationStatus.objects.all()
    serializer_class = JobApplicationStatusSerializer
    permission_classes = [IsEmployer | IsJobBoardAdmin]


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Allows filtering of applications based on user role (job seeker or employer)
        """
        user = self.request.user
        if user.is_staff:  # Admin or Employer can see all applications
            return JobApplication.objects.all()
        elif user.is_employer:
            return JobApplication.objects.filter(job__employer=user)
        return JobApplication.objects.filter(
            job_seeker=user
        )  # Job Seekers can see their own applications

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """
        Employer can update the status of a job application
        """
        job_application = self.get_object()
        status_code = request.data.get("status")
        status = JobApplicationStatus.objects.get(status_code=status_code)

        if job_application.job.employer != request.user:
            return Response(
                {"error": "Only the employer can update the application status."},
                status=403,
            )

        # Create a status history record
        status_history = JobApplicationStatusHistory.objects.create(
            job_application=job_application, status=status, changed_by=request.user
        )

        job_application.status = status
        job_application.save()

        return Response(JobApplicationSerializer(job_application).data)

    @action(detail=True, methods=["get"], url_path="status-history")
    def status_history(self, request, pk=None):
        """
        View the status history for a particular job application.
        """
        job_application = self.get_object()
        history = JobApplicationStatusHistory.objects.filter(
            job_application=job_application
        )
        serializer = JobApplicationStatusHistorySerializer(history, many=True)
        return Response(serializer.data)
