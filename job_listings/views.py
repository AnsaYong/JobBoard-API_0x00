from datetime import datetime
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
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
    API endpoint to manage industries with search support.

    ## Search & Filter:
    Example: `GET /industries/?search=Technology`
    You can search for industries based on the `name` attribute.
    This can be used to integrate a search-as-you-type functionality
    on the frontend.

    ## Permissions:
    - Read: **Open to everyone**
    - Write: **Restricted to authenticated users**
    """

    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Returns the queryset for industries based on the search query.

        If a search query is provided, it filters the industries based
        on the query. Otherwise, it returns all industries.

        Returns:
        - **Industry queryset**: A filtered queryset based on the search query.
        """
        search_query = self.request.query_params.get("search", None)
        queryset = super().get_queryset()

        if search_query:
            return queryset.filter(name__icontains=search_query)

        return queryset


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage job locations with search support.

    ## Search & Filter:
    Example: `GET /locations/?search=Johannesburg`
    You can search for locations based on the `city`, `postal_code`,
    `state_or_province`, and `country`. This can be used to integrate
    a search-as-you-type functionality on the frontend.

    ## Permissions:
    - Read: **Open to everyone**
    - Write: **Restricted to authenticated users**
    """

    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Returns the queryset for job locations based on the search query.

        If a search query is provided, it filters the locations based on the query.
        Otherwise, it returns all locations.

        Returns:
        - **Location queryset**: A filtered queryset based on the search query.
        """
        search_query = self.request.query_params.get("search", None)
        queryset = super().get_queryset()

        if search_query:
            return queryset.filter(
                Q(city__icontains=search_query)
                | Q(postal_code__icontains=search_query)
                | Q(state_or_province__icontains=search_query)
                | Q(country__icontains=search_query)
            )

        return queryset


class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage job-related skills with search support.

    ## Search & Filter:
    Example: `GET /skills/?search=Python`
    You can search for skills based on the `name` attribute.
    This can be used to integrate a search-as-you-type functionality
    on the frontend.

    ## Permissions:
    - Read: **Open to everyone**
    - Write: **Restricted to authenticated users**
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Returns the queryset for skills based on the search query.

        If a search query is provided, it filters the skills based on the query.
        Otherwise, it returns all skills.

        Returns:
        - **Skill queryset**: A filtered queryset based on the search query.
        """
        search_query = self.request.query_params.get("search", None)
        queryset = super().get_queryset()

        if search_query:
            return queryset.filter(name__icontains=search_query)

        return queryset


class CustomUserPagination(PageNumberPagination):
    """
    A custom pagination class for the User model.

    Allows users to set custom page sizes and navigate through the
    paginated results.

    **Attributes:**
    - `page_size`: (int) Number of items per page
    (overrides the global PAGE_SIZE in settings.py).
    - `page_size_query_param`: (str) URL query parameter to set the page size.
    - `max_page_size`: (int) Maximum number of items per page.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    API endpoint to create and manage job postings.

    It supports job filtering by category (location, industry, job_type),
    and full-text search on the job title and description.

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
    Users can filter by `location`, `industry`, and `job_type`
    using query parameters.
    - `GET /jobs/?industry={industry_id}` → Filter jobs by industry
    - `GET /jobs/?location={location_id}` → Filter jobs by location
    - `GET /jobs/?job_type={job_type}` → Filter jobs by job type
    - `GET /jobs/?industry=tech&location=1&job_type=full-time` → Combined filter

    **Searching:**
    Users can search using keywords in `title` and `description`
    - `GET /jobs/?search=Python` → Search for jobs with "Python" in the title or description
    - `GET /jobs/?search=python%20developer` → Search for jobs with "python" and "developer"

    **Permissions:**
    - **Superuser**: Full access to all job postings.
    - **Employers**: Can view and manage their own job postings.
    - **Job Seekers**: Can only view active job postings.
    - **Admins**: Full access to manage job postings.

    """

    serializer_class = JobPostingSerializer
    pagination_class = CustomUserPagination

    queryset = (
        JobPosting.objects.select_related("industry", "location", "employer")
        .prefetch_related("skills_required")
        .order_by("-posted_at")
    )

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = JobPostingFilter

    search_fields = ["title", "description"]  # Full-text search
    filterset_fields = ["location", "industry", "job_type"]  # Filtering
    ordering_fields = ["posted_at", "expiration_date"]  # Ordering

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
        Caching for job postings is implemented to reduce database queries.

        - **Superusers** can view all job postings.
        - **Regular users** (Job Seekers and Employers) can only view job postings
            that are not expired (based on `expiration_date`).

        Returns:
        - **Job Posting queryset**: A filtered queryset based on the user's role and expiration date.
        """
        if getattr(self, "swagger_fake_view", False):
            return JobPosting.objects.none()

        search_query = self.request.query_params.get("search", None)
        cache_key = f"job_postings_{search_query or 'all'}"

        # Try to get cached data
        cached_data = cache.get(cache_key)
        if cached_data:
            return JobPosting.objects.filter(job_id__in=cached_data)

        # if not cached, get the queryset
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == "employer":
            queryset = queryset.filter(employer=user)

        if user.role == "jobseeker":
            queryset = queryset.filter(is_active=True).filter(
                expiration_date__gte=datetime.now()
            )

        if search_query:
            search_vector = SearchVector("title", "description")
            search_query = SearchQuery(search_query)
            queryset = queryset.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3)

        # Cache job IDs for 5 minutes
        job_ids = list(queryset.values_list("job_id", flat=True))
        cache.set(cache_key, job_ids, timeout=300)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Cachiing individual job postings for 5 minutes."""
        cache_key = f"job_posting_{kwargs['pk']}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes

        return response

    def perform_create(self, serializer):
        """
        Override the perform_create method to automatically assign the employer
        to the job posting when it is created.

        The employer is assigned based on the authenticated user making the request.

        Cached data is cleared when a new job posting is created.

        Arguments:
        - **serializer**: The validated data for the job posting.
        """
        cache.delete("job_postings_all_serialized")
        cache.delete("job_postings_search_*")
        serializer.save(employer=self.request.user)

    def perform_update(self, serializer):
        """
        Override the perform_update method to clear cached data when a job posting is updated.

        Arguments:
        - **serializer**: The validated data for the job posting.
        """
        cache.delete("job_postings_all_serialized")
        cache.delete("job_postings_search_*")
        serializer.save()

    def delete(self, request, *args, **kwargs):
        """
        Soft delete a job posting by calling the `delete_job` method on the instance.

        Arguments:
        - **request**: The request listed job object.
        - **args**: Additional arguments.
        - **kwargs**: Additional keyword arguments.
        """
        cache.delete("job_postings_all_serialized")
        cache.delete("job_postings_search_*")

        instance = self.get_object()
        instance.delete_job()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
