from datetime import datetime
from rest_framework import viewsets, permissions
from django_filters import rest_framework as filters
from .models import JobPosting, Location, Industry, Skill
from .serializers import (
    JobPostingSerializer,
    LocationSerializer,
    IndustrySerializer,
    SkillSerializer,
)
from .filters import JobPostingFilter
from permissions import IsJobseeker, IsEmployer, IsJobBoardAdmin


class IndustryViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage industries.

    ## Endpoints:
    - `GET /industries/` → List all industries
    - `POST /industries/` → Create a new industry
    - `GET /industries/{id}/` → Retrieve an industry by ID
    - `PUT /industries/{id}/` → Update an industry
    - `DELETE /industries/{id}/` → Delete an industry

    ## Permissions:
    - Read: **Open to everyone**
    - Write: **Restricted to authenticated users**
    """

    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    # permission_classes = [permissions.IsAuthenticated]


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage job locations.

    ## Endpoints:
    - `GET /locations/` → List all locations
    - `POST /locations/` → Create a new location
    - `GET /locations/{id}/` → Retrieve a location by ID
    - `PUT /locations/{id}/` → Update a location
    - `DELETE /locations/{id}/` → Delete a location

    ## Permissions:
    - Read: **Open to everyone**
    - Write: **Restricted to authenticated users**
    """

    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    # permission_classes = [permissions.IsAuthenticated]


class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage job-related skills.

    ## Endpoints:
    - `GET /skills/` → List all skills
    - `POST /skills/` → Create a new skill
    - `GET /skills/{id}/` → Retrieve a skill by ID
    - `PUT /skills/{id}/` → Update a skill
    - `DELETE /skills/{id}/` → Delete a skill

    ## Permissions:
    - Read: **Open to everyone**
    - Write: **Restricted to authenticated users**
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    # permission_classes = [permissions.IsAuthenticated]


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    API endpoint to create and manage job postings.

    It supports filtering job postings based on various attributes such
    as job title, location, industry, job type, and expiration date.

    **Permissions**:
    - **List/Read**: Available to Job Seekers, Employers, and Admins.
    - **Create/Update/Delete**: Restricted to Employers and Admins.

    **Example Request Format:**
    - **POST** `api/jobs/` (Create a new job posting)
    ```json
    {
        "title": "Software Engineer",
        "description": "Looking for an experienced Python/Django developer.",
        "job_type": "full-time",
        "location": {
            "city": "Pretoria",
            "postal_code": "94105",
            "country": "South Africa"
        },
        "industry": {
            "name": "Technology"
        },
        "skills_required": [
            {"name": "Python"},
            {"name": "Django"},
            {"name": "REST API"}
        ],
        "salary_min": "80000.00",
        "salary_max": "120000.00",
        "expiration_date": "2025-12-31T23:59:59Z"
    }
    ```

    **Example Response Format:**
    - **GET** `api/jobs/` (Retrieve job postings)
    ```json
    {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
        "job_id": "a72b236e-04fa-4d25-9284-d48528068449",
        "employer": "880058aa-9758-4983-978f-74f3523bbbcd",
        "title": "Software Engineer",
        "slug": "software-engineer",
        "description": "Looking for an experienced Python/Django developer.",
        "job_type": "full-time",
        "location": {
            "location_id": "a5fe13cc-3a9b-4117-a9d7-1d33289eff6a",
            "city": "Pretoria",
            "postal_code": "94105",
            "state_or_province": null,
            "country": "South Africa"
        },
        "industry": {
            "industry_id": "b4b726f9-011b-4c08-a825-39177debb70e",
            "name": "Technology"
        },
        "skills_required": [
            {
            "skill_id": "111790fa-40f4-4251-a19e-84537808b74c",
            "name": "Django"
            },
            {
            "skill_id": "047639e9-d3eb-48aa-a55d-9a0c0253c623",
            "name": "Python"
            },
            {
            "skill_id": "1b5f53c1-2d83-4859-b2db-f3e62906c7f3",
            "name": "REST API"
            }
        ],
        "salary_min": "80000.00",
        "salary_max": "120000.00",
        "currency": "ZAR",
        "expiration_date": "2025-12-31T23:59:59Z",
        "posted_at": "2025-03-06T10:46:31.892128Z",
        "updated_at": "2025-03-06T10:46:31.892132Z",
        "is_active": true
        }
      ]
    }
    ```

    **Filtering:**
    You can filter job postings based on `title`, `location`, `industry`,
    `job_type`, and `expiration_date` using query parameters.
    - `GET /jobs/?industry={industry_id}` → Filter jobs by industry
    - `GET /jobs/?location={location_id}` → Filter jobs by location
    - `GET /jobs/?job_type={job_type}` → Filter jobs by job type


    **Permissions:**
    - **Superuser**: Full access to all job postings.
    - **Employers**: Can view and manage their own job postings.
    - **Job Seekers**: Can only view active job postings.
    - **Admins**: Full access to manage job postings.

    """

    queryset = JobPosting.objects.filter(is_active=True).order_by("-posted_at")
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
            return self.queryset

        return self.queryset.filter(expiration_date__gte=datetime.now())

    def perform_create(self, serializer):
        """
        Override the perform_create method to automatically assign the employer
        to the job posting when it is created.

        The employer is assigned based on the authenticated user making the request.

        Arguments:
        - **serializer**: The validated data for the job posting.
        """
        print("In perform_create method")
        serializer.save(employer=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Soft delete a job posting by calling the `delete_job` method on the instance.

        Arguments:
        - **request**: The request listed job object.
        - **args**: Additional arguments.
        - **kwargs**: Additional keyword arguments.
        """
        instance = self.get_object()
        instance.delete_job()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
