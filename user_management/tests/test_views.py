import pytest
from datetime import timedelta
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .factories import UserFactory

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


@pytest.mark.django_db
class TestPasswordResetRequestView:
    """Tests for the Password Reset Request API."""

    @pytest.fixture
    def password_reset_url(self):
        """Returns the password reset request URL."""
        return reverse("password_reset")

    def test_password_reset_valid_email(
        self, client, password_reset_url, jobseeker_user
    ):
        """Test requesting a password reset for a valid email."""
        email = jobseeker_user.email
        uid = urlsafe_base64_encode(force_bytes(jobseeker_user.pk))
        token = PasswordResetTokenGenerator().make_token(jobseeker_user)
        expected_reset_link = f"https://frontend.com/reset-password/{uid}/{token}/"

        with patch(
            "user_management.tasks.send_password_reset_email.delay"
        ) as mock_task:
            response = client.post(password_reset_url, {"email": email}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password reset link sent to your email."
        mock_task.assert_called_once_with(email, expected_reset_link)

    def test_password_reset_invalid_email(self, client, password_reset_url):
        """Test requesting a password reset with an email that does not exist."""

        with patch(
            "user_management.tasks.send_password_reset_email.delay"
        ) as mock_task:
            response = client.post(
                password_reset_url, {"email": "nonexistent@email.com"}, format="json"
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_task.assert_not_called()  # Ensure no email is sent

    def test_password_reset_missing_email(self, client, password_reset_url):
        """Test requesting a password reset without providing an email."""
        response = client.post(password_reset_url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Tests for the Password Reset Confirm API."""

    @pytest.fixture
    def user(self, user_data):
        """Creates and returns a user for the test."""
        user = get_user_model().objects.create_user(**user_data)
        return user

    @pytest.fixture
    def password_reset_confirm_url(self):
        """Returns the password reset confirm request URL."""
        return reverse("password_reset_confirm")

    def test_successful_password_reset(self, client, password_reset_confirm_url, user):
        """Test successful password reset when valid data is provided."""
        user.set_password("oldpassword123")
        user.save()

        # Generate valid token for the user
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        new_password = "@newpassword123"

        # Perform password reset request
        response = client.post(
            password_reset_confirm_url,
            {"uid": uid, "token": token, "new_password": new_password},
            format="json",
        )

        # Assert the response is successful
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password reset successfully."

        # Verify the user's password is updated
        user.refresh_from_db()
        assert user.check_password(new_password)

    def test_invalid_user(self, client, password_reset_confirm_url, user):
        """Test password reset with an invalid user."""
        # Generate a valid token for the existing user
        token_generator = PasswordResetTokenGenerator()
        valid_token = token_generator.make_token(user)
        valid_uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Use an invalid uid (non base64 or incorrect encoding)
        invalid_uid = "invalid-uid"  # Invalid base64-encoded string for UID

        new_password = "@newpassword123"

        response = client.post(
            password_reset_confirm_url,
            {"uid": invalid_uid, "token": valid_token, "new_password": new_password},
            format="json",
        )

        # Assert the response indicates an invalid user
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Invalid user"

    def test_invalid_token(self, client, password_reset_confirm_url, user):
        """Test attempting to reset the password with an invalid or expired token."""
        user.set_password("oldpassword123")
        user.save()

        # Generate a valid token but modify it to make it invalid
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        invalid_token = token + "invalid"

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        new_password = "@newpassword123"

        response = client.post(
            password_reset_confirm_url,
            {"uid": uid, "token": invalid_token, "new_password": new_password},
            format="json",
        )

        # Assert the response indicates an invalid or expired token
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Invalid or expired token"

    def test_empty_password(self, client, password_reset_confirm_url, user):
        """Test attempting to reset the password with an empty new password."""
        user.set_password("oldpassword123")
        user.save()

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = client.post(
            password_reset_confirm_url,
            {"uid": uid, "token": token, "new_password": ""},
            format="json",
        )

        # Assert the response indicates that the password is invalid
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data

    def test_password_not_matching_policy(
        self, client, password_reset_confirm_url, user
    ):
        """Test attempting to reset the password with a password that doesn't match the policy."""
        user.set_password("oldpassword123")
        user.save()

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        invalid_password = "short"

        response = client.post(
            password_reset_confirm_url,
            {"uid": uid, "token": token, "new_password": invalid_password},
            format="json",
        )

        # Assert the response indicates that the password doesn't meet the policy
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Password must be at least 8 characters long." in response.data["error"]

    def test_missing_field(self, client, password_reset_confirm_url, user):
        """Test attempting to reset the password with missing fields in the request."""
        user.set_password("oldpassword123")
        user.save()

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Missing new_password field
        response = client.post(
            password_reset_confirm_url,
            {"uid": uid, "token": token},
            format="json",
        )

        # Assert the response indicates that a required field is missing
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data


@pytest.mark.django_db
class TestPasswordChangeView:
    """Tests for the Password Change API."""

    @pytest.fixture
    def password_change_url(self):
        """Returns the password change request URL."""
        return reverse("password_change")

    def test_successful_password_change(
        self, api_client, jobseeker_user, password_change_url
    ):
        """Test that an authenticated user can successfully change their password."""
        jobseeker_user.set_password("oldpassword123")
        jobseeker_user.save()

        api_client.force_authenticate(user=jobseeker_user)

        new_password = "Newpass123!"
        response = api_client.put(
            password_change_url,
            {"old_password": "oldpassword123", "new_password": new_password},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password changed successfully."

        # Verify password was updated
        jobseeker_user.refresh_from_db()
        assert jobseeker_user.check_password(new_password)

    def test_incorrect_old_password(
        self, api_client, jobseeker_user, password_change_url
    ):
        """Test that providing an incorrect old password returns an error."""
        jobseeker_user.set_password("correctpassword123")
        jobseeker_user.save()

        api_client.force_authenticate(user=jobseeker_user)

        response = api_client.put(
            password_change_url,
            {"old_password": "wrongpassword", "new_password": "Newpass123!"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "old_password" in response.data
        )  # Assuming serializer returns field errors

    def test_missing_fields(self, api_client, jobseeker_user, password_change_url):
        """Test that missing fields in the request results in an error."""
        jobseeker_user.set_password("oldpassword123")
        jobseeker_user.save()

        api_client.force_authenticate(user=jobseeker_user)

        response = api_client.put(
            password_change_url, {"old_password": "oldpassword123"}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data  # Missing field error

    def test_password_not_meeting_policy(
        self, api_client, jobseeker_user, password_change_url
    ):
        """Test that a new password not meeting the policy returns an error."""
        jobseeker_user.set_password("oldpassword123")
        jobseeker_user.save()

        api_client.force_authenticate(user=jobseeker_user)

        invalid_password = "short"

        response = api_client.put(
            password_change_url,
            {"old_password": "oldpassword123", "new_password": invalid_password},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Password must be at least 8 characters long."
            in response.data["new_password"]
        )

    # def test_unauthorized_user_cannot_change_password(
    #     self, api_client, password_change_url
    # ):
    #     """Test that an unauthenticated user cannot change the password."""
    #     response = api_client.put(
    #         password_change_url,
    #         {"old_password": "oldpassword123", "new_password": "Newpass123!"},
    #         format="json",
    #     )

    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserView:
    """Tests for the User View API."""

    def test_admin_can_see_all_users(
        self, api_client, admin_user, employer_user, jobseeker_user
    ):
        """Test that an admin user can see all users."""
        api_client.force_authenticate(user=admin_user)
        users_list_url = reverse("user-list")

        response = api_client.get(users_list_url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 3  # Admin should see all users
        returned_emails = {user["email"] for user in response.data["results"]}
        expected_emails = {admin_user.email, employer_user.email, jobseeker_user.email}
        assert returned_emails == expected_emails  # Ensure all users are listed

    def test_employer_can_only_see_their_profile(
        self, api_client, employer_user, jobseeker_user
    ):
        """Test that an employer can only see their own profile."""
        api_client.force_authenticate(user=employer_user)
        users_list_url = reverse("user-list")

        response = api_client.get(users_list_url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["email"] == employer_user.email

    def test_employer_can_retrieve_own_profile(
        self, api_client, employer_user, jobseeker_user
    ):
        """Test that an employer can only retrieve their own profile."""
        api_client.force_authenticate(user=employer_user)
        users_detail_url = reverse("user-detail", args=[employer_user.pk])

        response = api_client.get(users_detail_url)

        assert response.status_code == 200
        assert response.data["email"] == employer_user.email

    def test_employer_cannot_retrieve_other_users(
        self, api_client, employer_user, jobseeker_user
    ):
        """Test that an employer cannot retrieve another user's profile."""
        api_client.force_authenticate(user=employer_user)
        users_detail_url = reverse("user-detail", args=[jobseeker_user.pk])

        response = api_client.get(users_detail_url)

        assert (
            response.status_code == 404
        )  # Only a user's profile is returned, unless admin

    def test_jobseeker_can_only_view_own_profile(
        self, api_client, jobseeker_user, employer_user
    ):
        """Test that a jobseeker user can only view their own profile."""
        api_client.force_authenticate(user=jobseeker_user)
        users_detail_url = reverse("user-detail", args=[jobseeker_user.pk])

        response = api_client.get(users_detail_url)
        assert response.status_code == status.HTTP_200_OK

        users_detail_url = reverse("user-detail", args=[employer_user.pk])
        response = api_client.get(users_detail_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_access_users(self, api_client):
        """Test that an unauthenticated user cannot access the users endpoint."""
        users_list_url = reverse("user-list")

        response = api_client.get(users_list_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_admin_can_create_user(self, api_client, admin_user):
        """Test that an admin user can create a new user."""
        api_client.force_authenticate(user=admin_user)
        users_list_url = reverse("user-list")

        data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
            "role": "jobseeker",
        }
        response = api_client.post(users_list_url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_create_user_missing_fields(self, api_client, admin_user):
        """Test that an admin user cannot create a new user with missing fields."""
        api_client.force_authenticate(user=admin_user)
        users_list_url = reverse("user-list")

        data = {
            "email": "newuser@example.com",
            "password": "password123",
            "role": "jobseeker",
        }
        response = api_client.post(users_list_url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "first_name" in response.data
        assert "last_name" in response.data

    def test_jobseeker_cannot_create_user(self, api_client, jobseeker_user):
        """Test that a jobseeker user cannot create a new user."""
        api_client.force_authenticate(user=jobseeker_user)
        users_list_url = reverse("user-list")

        data = {
            "email": "newuser@example.com",
            "password": "password123",
            "role": "jobseeker",
        }
        response = api_client.post(users_list_url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_can_deactivate_themselves(self, api_client, jobseeker_user):
        """Test that a user can deactivate their own account."""
        api_client.force_authenticate(user=jobseeker_user)
        users_list_url = reverse("user-deactivate", args=[jobseeker_user.pk])

        response = api_client.post(users_list_url)
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["message"]
            == "Your account has been deactivated successfully."
        )

    def test_user_cannot_deactivate_another_user(
        self, api_client, jobseeker_user, employer_user
    ):
        """Test that a user cannot deactivate another user's account."""
        api_client.force_authenticate(user=jobseeker_user)
        users_list_url = reverse("user-deactivate", args=[employer_user.pk])

        response = api_client.post(users_list_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_can_deactivate_other_user(
        self, api_client, admin_user, jobseeker_user
    ):
        """Test that an admin user can deactivate another user's account."""
        api_client.force_authenticate(user=admin_user)
        users_deativate_url = reverse("user-deactivate", args=[jobseeker_user.pk])

        response = api_client.post(users_deativate_url)
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["message"]
            == "Your account has been deactivated successfully."
        )

    def test_user_cannot_deactivate_if_already_deactivated(
        self, api_client, jobseeker_user
    ):
        """Test that a user cannot deactivate their account if it is already deactivated."""
        jobseeker_user.is_active = False
        jobseeker_user.save()
        api_client.force_authenticate(user=jobseeker_user)
        users_deativate_url = reverse("user-deactivate", args=[jobseeker_user.pk])

        response = api_client.post(users_deativate_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Your account is already deactivated."

    def test_pagination_works(self, api_client, admin_user):
        """Test that pagination works for the users list."""
        for i in range(15):  # Create 15 users
            UserFactory.create(role="jobseeker")

        api_client.force_authenticate(user=admin_user)
        users_list_url = reverse("user-list")

        response = api_client.get(users_list_url, {"page_size": 5})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5
        assert "next" in response.data
        assert response.data["previous"] is None
