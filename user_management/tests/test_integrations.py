"""API-level tests for user management."""

import pytest
from django.urls import reverse
from rest_framework import status
from user_management.models import User


@pytest.mark.django_db
class TestUserManagementIntegration:
    """Full integration test for user registration, login, and profile update."""

    def test_user_registration_login_update(self, api_client):
        """Test a complete user workflow: register → login → update profile."""

        # Step 1: Register the user
        register_url = reverse("register")
        user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "jobseeker",
            "password": "Test@1234",
            "password2": "Test@1234",
        }
        reg_response = api_client.post(register_url, user_data)
        assert reg_response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data["email"]).exists()

        # Step 2: Log in with the new user
        login_url = reverse("login")
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        login_response = api_client.post(login_url, login_data)

        print(login_response.data)

        assert login_response.status_code == status.HTTP_200_OK
        assert "access_token" in login_response.data["data"]
        access_token = login_response.data["data"]["access_token"]

        print("Acces token:", access_token)

        # Step 3: Update user profile
        user = User.objects.get(email=user_data["email"])
        profile_url = reverse("user-detail", args=[user.user_id])

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        update_data = {"first_name": "Updated", "last_name": "Name"}

        update_response = api_client.patch(profile_url, update_data)

        assert update_response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"
