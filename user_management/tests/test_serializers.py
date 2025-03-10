import pytest
from unittest.mock import MagicMock
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from user_management.serializers import (
    RegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    UserSerializer,
)

User = get_user_model()


# Test the RegisterSerializer
@pytest.mark.django_db
def test_register_user_valid():
    """Test valid user registration"""
    data = {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "jobseeker",
        "password": "password123",
        "password2": "password123",
    }
    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.email == data["email"]
    assert user.first_name == data["first_name"]
    assert user.check_password(data["password"])


@pytest.mark.django_db
def test_register_user_missing_passwords():
    """Test that missing password fields raises validation error"""
    data = {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "jobseeker",
    }
    serializer = RegisterSerializer(data=data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_register_user_password_mismatch():
    """Test that password mismatch raises validation error"""
    data = {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "jobseeker",
        "password": "password123",
        "password2": "differentpassword",
    }
    serializer = RegisterSerializer(data=data)
    with pytest.raises(ValidationError, match="Passwords do not match."):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_register_user_invalid_role():
    """Test that an invalid role raises a validation error"""
    data = {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "invalid_role",
        "password": "password123",
        "password2": "password123",
    }
    serializer = RegisterSerializer(data=data)
    with pytest.raises(ValidationError, match='"invalid_role" is not a valid choice.'):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_register_user_existing_email():
    """Test that registering with an existing email raises a validation error"""
    User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )
    data = {
        "email": "testuser@email.com",
        "first_name": "Test2",
        "last_name": "User2",
        "role": "jobseeker",
        "password": "password123",
        "password2": "password123",
    }
    serializer = RegisterSerializer(data=data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_register_user_missing_email_field():
    """Test that missing an email field raises a validation error"""
    data = {
        "first_name": "Test",
        "role": "jobseeker",
        "password": "password123",
        "password2": "password123",
    }
    serializer = RegisterSerializer(data=data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


# Test the PasswordResetRequestSerializer
@pytest.mark.django_db
def test_password_reset_request_valid():
    """Test that sending a valid email for password reset works"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )
    data = {"email": user.email}
    serializer = PasswordResetRequestSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.validated_data["email"] == user.email


@pytest.mark.django_db
def test_password_reset_request_invalid_email():
    """Test that sending an invalid email returns an error"""
    data = {"email": "invalidemail@email.com"}
    serializer = PasswordResetRequestSerializer(data=data)

    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert serializer.errors["email"][0] == "User with this email does not exist."


@pytest.mark.django_db
def test_password_reset_request_empty_email():
    """Test that an empty email raises a validation error"""
    data = {"email": ""}
    serializer = PasswordResetRequestSerializer(data=data)

    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert serializer.errors["email"][0] == "This field may not be blank."


@pytest.mark.django_db
def test_password_reset_request_invalid_email_format():
    """Test that an invalid email format raises a validation error"""
    data = {"email": "invalid-email-format"}
    serializer = PasswordResetRequestSerializer(data=data)

    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert "Enter a valid email address." in serializer.errors["email"]


# Test the PasswordResetConfirmSerializer
@pytest.mark.django_db
def test_password_reset_confirm_valid():
    """Test that resetting the password with a valid UID and token works"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )

    # Generate a valid UID and token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)

    data = {
        "uid": uid,
        "token": token,
        "new_password": "newpassword123",
    }

    serializer = PasswordResetConfirmSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["uid"] == uid
    assert serializer.validated_data["token"] == token
    assert serializer.validated_data["new_password"] == "newpassword123"


@pytest.mark.django_db
def test_password_reset_confirm_valid_uid():
    """Test that a valid UID is correctly decoded"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    serializer = PasswordResetConfirmSerializer(
        data={"uid": uid, "token": "valid_token", "new_password": "newpassword123"}
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["uid"] == uid


@pytest.mark.django_db
def test_password_reset_confirm_valid_new_password():
    """Test that a valid new password is accepted"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)

    data = {
        "uid": uid,
        "token": token,
        "new_password": "strongnewpassword",
    }

    serializer = PasswordResetConfirmSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["new_password"] == "strongnewpassword"


# Test the PasswordChangeSerialier
@pytest.mark.django_db
def test_password_change_valid():
    """Test changing password with correct old password"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )

    mock_request = MagicMock()
    mock_request.user = user

    new_password = "newpassword123"
    data = {
        "old_password": "password123",
        "new_password": new_password,
    }

    serializer = PasswordChangeSerializer(data=data, context={"request": mock_request})
    assert serializer.is_valid()

    # Manually update the password in the user model after validation
    user.set_password(new_password)
    user.save()

    user.refresh_from_db()
    assert user.check_password(new_password)


@pytest.mark.django_db
def test_password_change_invalid_old_password():
    """Test that providing an incorrect old password raises a validation error"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )

    mock_request = MagicMock()
    mock_request.user = user

    data = {
        "old_password": "wrongpassword",
        "new_password": "newpassword123",
    }
    serializer = PasswordChangeSerializer(data=data, context={"request": mock_request})
    assert not serializer.is_valid()
    assert "old_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_empty_fields():
    """Test that empty fields raise a validation error"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )

    mock_request = MagicMock()
    mock_request.user = user

    # Empty old password
    data = {"old_password": "", "new_password": "newpassword123"}
    serializer = PasswordChangeSerializer(data=data, context={"request": mock_request})
    assert not serializer.is_valid()
    assert "old_password" in serializer.errors

    # Empty new password
    data = {"old_password": "password123", "new_password": ""}
    serializer = PasswordChangeSerializer(data=data, context={"request": mock_request})
    assert not serializer.is_valid()
    assert "new_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_same_as_old():
    """Test that changing to the same password is allowed"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )

    mock_request = MagicMock()
    mock_request.user = user

    data = {
        "old_password": "password123",
        "new_password": "password123",
    }
    serializer = PasswordChangeSerializer(data=data, context={"request": mock_request})

    assert serializer.is_valid()


# Test the UserSerializer
@pytest.mark.django_db
def test_user_serializer_valid():
    """Test user serialization and deserialization with valid data"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
        role="jobseeker",
    )
    serializer = UserSerializer(user)

    # Ensure serialized data matches the user object
    assert serializer.data["email"] == user.email
    assert serializer.data["first_name"] == user.first_name
    assert serializer.data["last_name"] == user.last_name
    assert serializer.data["role"] == user.role
    assert serializer.data["is_active"] == user.is_active
    assert "password" not in serializer.data  # Ensure password is not exposed


@pytest.mark.django_db
def test_user_serializer_invalid_role():
    """Test user serializer with an invalid role"""
    data = {
        "email": "testuser@email.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "invalid_role",
    }
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()
    assert "role" in serializer.errors


@pytest.mark.django_db
def test_user_serializer_invalid_email():
    """Test that an invalid email format is rejected"""
    data = {
        "email": "invalid-email",  # Not a valid email format
        "first_name": "Test",
        "last_name": "User",
        "role": "jobseeker",
    }
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors


@pytest.mark.django_db
def test_user_serializer_missing_fields():
    """Test that missing required fields raise validation errors"""

    # Missing email
    data = {"first_name": "Test", "last_name": "User", "role": "jobseeker"}
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors

    # Missing first name
    data = {"email": "testuser@email.com", "last_name": "User", "role": "jobseeker"}
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()
    assert "first_name" in serializer.errors

    # Missing last name
    data = {"email": "testuser@email.com", "first_name": "Test", "role": "jobseeker"}
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()
    assert "last_name" in serializer.errors


@pytest.mark.django_db
def test_user_serializer_read_only_fields():
    """Test that read-only fields cannot be modified"""
    user = User.objects.create_user(
        email="testuser@email.com",
        password="password123",
        first_name="Test",
        last_name="User",
        role="jobseeker",
        is_active=False,  # Initially inactive
    )

    data = {
        "email": "newemail@email.com",
        "first_name": "Updated",
        "last_name": "User",
        "role": "employer",
        "is_active": True,  # Attempting to modify read-only field
        "user_id": "12345",  # Attempting to modify read-only field
    }

    serializer = UserSerializer(user, data=data, partial=True)
    assert serializer.is_valid()

    updated_user = serializer.save()
    assert updated_user.email == "newemail@email.com"  # Should be updated
    assert updated_user.first_name == "Updated"  # Should be updated
    assert updated_user.role == "employer"  # Should be updated
    assert updated_user.is_active == False  # Should remain unchanged
    assert updated_user.user_id == user.user_id  # Should remain unchanged
