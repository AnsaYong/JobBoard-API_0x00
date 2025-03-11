import pytest
from django.utils import timezone
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from job_listings.models import Location, Industry, Skill, JobPosting


# Industry Model Tests
@pytest.mark.django_db
def test_create_industry(industry):
    """Test the creation of an industry."""
    assert industry.name == "NewTechnology"
    assert industry.created_at is not None


@pytest.mark.django_db
def test_industry_unique_name(industry):
    """Test that creating two industries with the same name raises an IntegrityError."""
    # First company is created already
    industry_data = {"name": "NewTechnology"}
    with pytest.raises(IntegrityError):
        Industry.objects.create(
            **industry_data
        )  # Create second industry with same name


@pytest.mark.django_db
def test_industry_string_representation(industry):
    """Test the string representation of the industry model."""
    assert str(industry) == "NewTechnology"


# Location Model Tests
@pytest.mark.django_db
def test_create_location(location):
    """Test the creation of a location."""
    assert location.city == "San Francisco"
    assert location.country == "USA"
    assert location.state_or_province == "NY"
    assert location.postal_code == "10001"


@pytest.mark.django_db
def test_location_string_representation(location):
    """Test the string representation of the location model."""
    assert str(location) == "San Francisco, USA"


# Skill Model Tests
@pytest.mark.django_db
def test_create_skill(skill):
    """Test the creation of a skill."""
    assert skill.name == "NewPython"


@pytest.mark.django_db
def test_skill_unique_name(skill):
    """Test that creating two skills with the same name raises an IntegrityError."""
    skill_data = {"name": "NewPython"}
    with pytest.raises(IntegrityError):
        Skill.objects.create(**skill_data)  # Create second skill with same name


@pytest.mark.django_db
def test_skill_string_representation(skill):
    """Test the string representation of the skill model."""
    assert str(skill) == "NewPython"


# Test JobListing model creation
@pytest.mark.django_db
def test_create_job_listing(job_listing):
    """Test job listing creation."""
    assert job_listing.title == "Software Developer"
    assert job_listing.company == "Tech Corp"
    assert job_listing.location.city == "San Francisco"
    assert job_listing.location.country == "USA"
    assert job_listing.location.state_or_province == "NY"
    assert job_listing.location.postal_code == "10001"
    print(job_listing.location)
    assert job_listing.industry.name == "NewTechnology"
    # assert job_listing.skills_required.count() == 1
    print(job_listing.skills_required)
    print(job_listing.skills_required.all())


@pytest.mark.django_db
def test_job_posting_creation(job_listing):
    """Test that a job posting is correctly created."""
    # Ensure the job posting exists
    assert JobPosting.objects.count() == 1

    job = job_listing

    # Check that the job posting fields are correctly set
    assert job.title == "Software Developer"
    assert job.description == "We are looking for a software developer."
    assert job.job_type == "full-time"
    assert job.company == "Tech Corp"
    assert job.location.city == "San Francisco"
    assert job.location.country == "USA"
    assert job.industry.name == "NewTechnology"
    # assert job.skills_required.count() == 1
    # assert job.skills_required.first().name == "NewPython"
    assert job.employer.email == "testemployer@email.com"  # Employer details
    assert job.salary_min is None  # Check that salary is None if not set
    assert job.salary_max is None
    assert job.currency == "ZAR"
    assert job.is_active is True
    assert job.expiration_date is not None


@pytest.mark.django_db
def test_job_posting_str_method(job_listing):
    """Test the __str__ method of the JobPosting model."""
    job = job_listing
    expected_str = f"{job.title} - {job.company}"
    assert str(job) == expected_str


@pytest.mark.django_db
def test_job_posting_expiration(job_listing):
    """Test that expired job postings can be filtered correctly."""
    job = job_listing
    job.expiration_date = timezone.make_aware(timezone.datetime(2022, 12, 31, 0, 0))
    job.save()

    expired_jobs = JobPosting.objects.filter(expiration_date__lt=timezone.now())
    assert job in expired_jobs
    assert expired_jobs.count() == 1


@pytest.mark.django_db
def test_job_posting_delete_method(job_listing):
    """Test the delete_job method of the JobPosting model."""
    job = job_listing
    job.delete_job()
    assert job.is_active is False
    assert JobPosting.objects.count() == 1
