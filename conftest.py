import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from job_listings.tests.factories import (
    LocationFactory,
    IndustryFactory,
    SkillFactory,
    JobListingFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "admin@email.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "@password123",
        "role": "admin",
    }


@pytest.fixture
def jobseeker_data():
    return {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "@password123",
        "role": "jobseeker",
    }


@pytest.fixture
def employer_data():
    return {
        "email": "testemployer@email.com",
        "first_name": "Test",
        "last_name": "Employer",
        "password": "@password123",
        "role": "employer",
    }


@pytest.fixture
def admin_user(user_data):
    """Fixture for creating an admin user"""
    user_model = get_user_model()
    return user_model.objects.create_superuser(**user_data)


@pytest.fixture
def jobseeker_user(jobseeker_data):
    """Fixture for creating a regular user"""
    user_model = get_user_model()
    return user_model.objects.create_user(**jobseeker_data)


@pytest.fixture
def employer_user(employer_data):
    """Fixture for creating a regular user"""
    user_model = get_user_model()
    return user_model.objects.create_user(**employer_data)


@pytest.fixture
def location():
    """Fixture for creating a location."""
    return LocationFactory.create(
        city="San Francisco", country="USA", postal_code="10001", state_or_province="NY"
    )


@pytest.fixture
def industry():
    """Fixture for creating an industry."""
    return IndustryFactory.create(name="NewTechnology")


@pytest.fixture
def skill():
    """Fixture for creating a skill."""
    return SkillFactory.create(name="NewPython")


@pytest.fixture
def job_listing(location, industry, skill, employer_user):
    """Fixture for creating a job listing."""
    expiration_date = timezone.make_aware(timezone.datetime(2022, 12, 31, 0, 0))

    return JobListingFactory.create(
        employer=employer_user,
        title="Software Developer",
        description="We are looking for a software developer.",
        job_type="full-time",
        location=location,
        industry=industry,
        company="Tech Corp",
        skills_required=[skill],
        expiration_date=expiration_date,
    )
