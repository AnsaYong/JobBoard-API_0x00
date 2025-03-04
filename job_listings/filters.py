from django_filters import rest_framework as filters
from .models import JobPosting


class JobPostingFilter(filters.FilterSet):
    """
    A filter class for job postings.
    This allows filtering based on title, job type, location, industry, etc.
    """

    title = filters.CharFilter(
        lookup_expr="icontains"
    )  # Case-insensitive search for title
    job_type = filters.CharFilter(
        field_name="job_type__name", lookup_expr="exact"
    )  # Filter by job type
    location_city = filters.CharFilter(field_name="location__city", lookup_expr="exact")
    location_state = filters.CharFilter(
        field_name="location__state", lookup_expr="exact"
    )
    location_country = filters.CharFilter(
        field_name="location__country", lookup_expr="exact"
    )
    industry = filters.CharFilter(field_name="industry__name", lookup_expr="exact")
    skills_required = filters.CharFilter(
        lookup_expr="icontains"
    )  # Filter based on required skills
    salary_range = filters.CharFilter(lookup_expr="exact")
    expiration_date = filters.DateFilter(lookup_expr="exact")
    posted_at = filters.DateTimeFilter(lookup_expr="exact")
    updated_at = filters.DateTimeFilter(lookup_expr="exact")

    # Allow filtering by range for expiration and other date-related fields
    expiration_date__lt = filters.DateFilter(
        field_name="expiration_date", lookup_expr="lt"
    )
    expiration_date__gt = filters.DateFilter(
        field_name="expiration_date", lookup_expr="gt"
    )
    posted_at__lt = filters.DateTimeFilter(field_name="posted_at", lookup_expr="lt")
    posted_at__gt = filters.DateTimeFilter(field_name="posted_at", lookup_expr="gt")
    updated_at__lt = filters.DateTimeFilter(field_name="updated_at", lookup_expr="lt")
    updated_at__gt = filters.DateTimeFilter(field_name="updated_at", lookup_expr="gt")

    class Meta:
        model = JobPosting
        fields = [
            "title",
            "job_type",
            "location_city",
            "location_state",
            "location_country",
            "industry",
            "skills_required",
            "salary_range",
            "expiration_date",
            "posted_at",
            "updated_at",
        ]
