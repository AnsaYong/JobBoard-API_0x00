import pytest
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestRegisterView:
    def setup_method(self):
        """Setup test client"""
        self.client = APIClient()
        self.register_url = reverse("register")

    def test_register_user_successful(self, jobseeker_data):
        """Test successful user registration"""
        jobseeker_data["password2"] = jobseeker_data["password"]
        response = self.client.post(self.register_url, jobseeker_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "Successful user registration!"
        assert User.objects.filter(email=jobseeker_data["email"]).exists()

    def test_register_user_already_exists(self, jobseeker_user, jobseeker_data):
        """Test that trying to register with an existing email fails"""
        # Passing jobseeker_data to the fixture will cause the user to be created
        jobseeker_data["password2"] = jobseeker_data["password"]
        response = self.client.post(self.register_url, jobseeker_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_user_password_mismatch(self, jobseeker_data):
        """Test that trying to register with mismatched passwords fails"""
        jobseeker_data["password2"] = "mismatchedpassword"
        response = self.client.post(self.register_url, jobseeker_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_register_user_missing_field(self, jobseeker_data):
        """Test that trying to register with missing fields fails"""
        jobseeker_data.pop("email")
        response = self.client.post(self.register_url, jobseeker_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "This field is required." in response.data["email"]

    def test_register_user_invalid_role(self, jobseeker_data):
        """Test that trying to register with an invalid role fails"""
        jobseeker_data["role"] = "invalidrole"
        response = self.client.post(self.register_url, jobseeker_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "role" in response.data

    def test_register_user_no_role(self, jobseeker_data):
        """Test that trying to register with no role fails"""
        jobseeker_data.pop("role")
        response = self.client.post(self.register_url, jobseeker_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "role" in response.data

    def test_register_user_no_password(self, jobseeker_data):
        """Test that trying to register with no password fails"""
        jobseeker_data.pop("password")
        response = self.client.post(self.register_url, jobseeker_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data


@pytest.mark.django_db
class TestLoginView:
    @pytest.fixture
    def login_url(self):
        return reverse("login")

    def test_successful_login(self, client, login_url, jobseeker_user, jobseeker_data):
        """Test logging in with correct credentials"""
        response = client.post(
            login_url,
            {"email": jobseeker_data["email"], "password": jobseeker_data["password"]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data["data"]
        assert "refresh_token" in response.data["data"]
        assert response.data["message"] == "User authenticated successfully"

    def test_login_invalid_password(
        self, client, login_url, jobseeker_user, jobseeker_data
    ):
        """Test login failure due to incorrect password"""
        response = client.post(
            login_url,
            {"email": jobseeker_data["email"], "password": "wrongpassword"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["message"] == "Invalid email or password"
        assert response.data["status"] == "error"

    def test_login_non_existent_email(self, client, login_url):
        """Test login failure due to non-existent email"""
        response = client.post(
            login_url,
            {"email": "doesnotexist@email.com", "password": "password123"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["message"] == "Invalid email or password"
        assert response.data["status"] == "error"

    def test_login_missing_email(self, client, login_url, jobseeker_user):
        """Test login failure due to missing email field"""
        response = client.post(
            login_url,
            {"password": "password123"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["message"] == "Invalid email or password"

    def test_login_missing_password(
        self, client, login_url, jobseeker_user, jobseeker_data
    ):
        """Test login failure due to missing password field"""
        response = client.post(
            login_url,
            {"email": jobseeker_data["email"]},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["message"] == "Invalid email or password"

    def test_login_empty_email_or_password(self, client, login_url, jobseeker_user):
        """Test login failure due to empty email or password"""
        response = client.post(
            login_url,
            {"email": "", "password": ""},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["message"] == "Invalid email or password"


@pytest.mark.django_db
class TestLogoutView:
    @pytest.fixture
    def logout_url(self):
        return reverse("logout")

    @pytest.fixture
    def auth_tokens(self, jobseeker_user):
        """Fixture to generate valid access and refresh tokens for a user."""
        refresh = RefreshToken.for_user(jobseeker_user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    def test_successful_logout(self, client, logout_url, auth_tokens):
        """Test that a valid refresh token is blacklisted upon logout."""
        headers = {"HTTP_AUTHORIZATION": f"Bearer {auth_tokens['access_token']}"}

        response = client.post(
            logout_url,
            {"refresh_token": auth_tokens["refresh_token"]},
            format="json",
            **headers,
        )
        assert response.status_code == status.HTTP_205_RESET_CONTENT
        assert response.data["message"] == "Successfully logged out"

    def test_logout_with_invalid_token(self, client, logout_url, auth_tokens):
        """Test logout with an invalid refresh token fails."""
        headers = {"HTTP_AUTHORIZATION": f"Bearer {auth_tokens['access_token']}"}

        response = client.post(
            logout_url,
            {"refresh_token": "invalid_refresh_token"},
            format="json",
            **headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_logout_without_token(self, client, logout_url, auth_tokens):
        """Test logout without providing a refresh token fails."""
        headers = {"HTTP_AUTHORIZATION": f"Bearer {auth_tokens['access_token']}"}

        response = client.post(logout_url, {}, format="json", **headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_logout_with_expired_token(self, client, logout_url, auth_tokens):
        """Test logout with an expired refresh token."""
        expired_token = RefreshToken(auth_tokens["refresh_token"])
        expired_token.set_exp(lifetime=timedelta(seconds=-1))

        headers = {"HTTP_AUTHORIZATION": f"Bearer {auth_tokens['access_token']}"}

        response = client.post(
            logout_url,
            {"refresh_token": str(expired_token)},
            format="json",
            **headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
