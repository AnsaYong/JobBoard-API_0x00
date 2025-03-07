import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user_data():
    return {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password123",
        "role": "jobseeker",
    }


@pytest.fixture
def jobseeker_user(user_data):
    """Fixture for creating a regular user"""
    user_model = get_user_model()
    return user_model.objects.create_user(**user_data)


@pytest.fixture
def admin_user(user_data):
    """Fixture for creating an admin user"""
    user_model = get_user_model()
    return user_model.objects.create_superuser(**user_data)
