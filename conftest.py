import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user_data():
    return {
        "email": "admin@email.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "password123",
        "role": "admin",
    }


@pytest.fixture
def jobseeker_data():
    return {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password123",
        "role": "jobseeker",
    }


@pytest.fixture
def employer_data():
    return {
        "email": "testemployer@email.com",
        "first_name": "Test",
        "last_name": "Employer",
        "password": "password123",
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
