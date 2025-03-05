from rest_framework import viewsets
from rest_framework import permissions
from django_filters import rest_framework as filters
from .models import JobPosting, Location, Industry
from .serializers import JobPostingSerializer, LocationSerializer, IndustrySerializer
from permissions import IsJobseeker, IsEmployer, IsJobBoardAdmin
from .filters import JobPostingFilter
from datetime import datetime


class IndustryViewSet(viewsets.ModelViewSet):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing job postings on the job board.

    This viewset allows users to interact with job postings by providing functionalities
    like creating, retrieving, updating, and deleting job postings. It also supports
    filtering job postings based on various attributes such as job title, location,
    industry, job type, and expiration date.

    Permissions:
    - **List/Read**: Available to Job Seekers, Employers, and Admins.
    - **Create/Update/Delete**: Restricted to Employers and Admins.

    **Example Request Format:**
    - **POST** `api/jobs/` (Create a new job posting)
    ```json
    {
        "title": "Software Engineer",
        "description": "We are looking for a skilled Software Engineer.",
        "job_type": "part-time" or "full-time" or "contract" or "internship" or "remote",
        "location": "<location-uuid>",
        "industry": "<industry-uuid>",
        "skills_required": ["Python", "Django"],
        "salary_range": "USD 80,000 - 100,000",
        "expiration_date": "2025-12-31T23:59:59Z"
    }
    ```

    **Example Response Format:**
    - **GET** `api/jobs/` (Retrieve job postings)
    ```json
    [
        {
            "job_id": "uuid-1234",
            "employer": "user-uuid-5678",
            "title": "Software Engineer",
            "description": "We are looking for a skilled Software Engineer.",
            "job_type": "full-time",
            "location": "<location-uuid>",
            "industry": "<industry-uuid>",
            "skills_required": ["Python", "Django"],
            "salary_range": "USD 80,000 - 100,000",
            "expiration_date": "2025-12-31T23:59:59Z",
            "posted_at": "2025-03-04T08:00:00Z",
            "updated_at": "2025-03-04T08:00:00Z"
        }
    ]
    ```

    **Filtering:**
    - You can filter job postings based on `title`, `location`, `industry`, `job_type`, and `expiration_date` using query parameters.

    **Permissions:**
    - **Superuser**: Full access to all job postings.
    - **Employers**: Can view and manage their own job postings.
    - **Job Seekers**: Can only view active job postings.
    - **Admins**: Full access to manage job postings.

    """

    serializer_class = JobPostingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = JobPostingFilter

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.

        Permissions depend on the action being performed:
        - **list/retrieve**: Available to Job Seekers, Employers, and Admins.
        - **create/update/delete**: Restricted to Employers and Admins.
        """
        user = self.request.user

        if user.is_superuser:
            return [permissions.AllowAny()]

        if self.action in ["list", "retrieve"]:
            permission_classes = [IsJobseeker | IsEmployer | IsJobBoardAdmin]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsEmployer | IsJobBoardAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Returns the queryset for job postings based on the user's role.

        - **Superusers** can view all job postings.
        - **Regular users** (Job Seekers and Employers) can only view job postings
          that are not expired (based on `expiration_date`).

        Returns:
        - **Job Posting queryset**: A filtered queryset based on the user's role and expiration date.
        """
        user = self.request.user

        if user.is_superuser:
            return JobPosting.objects.all()

        return JobPosting.objects.filter(expiration_date__gte=datetime.now())

    def perform_create(self, serializer):
        """
        Override the perform_create method to automatically assign the employer
        to the job posting when it is created.

        The employer is assigned based on the authenticated user making the request.

        Arguments:
        - **serializer**: The validated data for the job posting.
        """
        employer = self.request.user
        validated_data = serializer.validated_data.copy()
        validated_data["employer"] = employer

        serializer.save(**validated_data)
