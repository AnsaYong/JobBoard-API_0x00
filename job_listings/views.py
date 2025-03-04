from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import JobPosting
from .serializers import JobPostingSerializer
from permissions import IsJobseeker, IsEmployer, IsJobBoardAdmin
from .filters import JobPostingFilter
from datetime import datetime


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing job postings.
    This allows filtering by various job attributes such as title, location, industry, etc.
    """

    serializer_class = JobPostingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = JobPostingFilter

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        user = self.request.user
        if user.is_superuser:
            return []

        if self.action in ["list", "retrieve"]:
            permission_classes = [IsJobseeker]
        else:
            permission_classes = [IsEmployer]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Returns the queryset for job postings based on the user's role.
        Admin can view all, while regular users can only view active job postings.
        """
        user = self.request.user

        # Admin can view all job postings
        if user.is_staff:
            return JobPosting.objects.all()

        # Regular job seekers or employers can only see active job postings
        return JobPosting.objects.filter(expiration_date__gte=datetime.now())

    def perform_create(self, serializer):
        """
        Override the perform_create method to automatically assign the employer
        to the job posting.
        """
        serializer.save(employer=self.request.user)
