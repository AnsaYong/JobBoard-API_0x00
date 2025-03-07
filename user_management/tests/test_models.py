import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from user_management.tests.factories import UserFactory


# Test user instance creation
@pytest.mark.django_db
def test_create_user(user_data):
    """Test user creation."""
    user_model = get_user_model()
    user = user_model.objects.create_user(**user_data)
    assert user.email == user_data["email"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert user.role == user_data["role"]
    assert user.check_password(user_data["password"])  # Check password hash
    assert user.created_at is not None
    assert user.updated_at is not None


# Test superuser/JobBoardAdmin creation
@pytest.mark.django_db
def test_create_superuser(admin_user):
    """Test superuser creation."""
    user = admin_user
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_create_superuser_without_is_staff():
    """Test that creating a superuser without is_staff=True raises an error."""
    user_model = get_user_model()
    with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
        user_model.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="password123",
            is_staff=False,
        )


@pytest.mark.django_db
def test_create_superuser_without_is_superuser():
    """Test that creating a superuser without is_superuser=True raises an error."""
    user_model = get_user_model()
    with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
        user_model.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="password123",
            is_superuser=False,
        )


# Test field validation
@pytest.mark.django_db
def test_user_creation_without_email():
    """Test that creating a user without email raises an error."""
    user_model = get_user_model()
    with pytest.raises(ValueError, match="The Email field must be set"):
        user_model.objects.create_user(
            email="", first_name="Test", last_name="User", password="password123"
        )


@pytest.mark.django_db
def test_user_unique_email_constraint(user_data):
    """Test that creating two users with the same email raises an IntegrityError."""
    user_model = get_user_model()
    user_model.objects.create_user(**user_data)  # Create first user
    with pytest.raises(IntegrityError):
        user_model.objects.create_user(
            **user_data
        )  # Create second user with same email


@pytest.mark.django_db
def test_invalid_user_role(user_data):
    """Test that creating a user with an invalid role raises an error."""
    user_model = get_user_model()
    user_data["role"] = "invalid_role"

    user = user_model(**user_data)
    with pytest.raises(ValidationError):
        user.full_clean()  # This will trigger the validation and raise the error


# Test user model methods
@pytest.mark.django_db
def test_user_get_full_name(jobseeker_user):
    """Test the get_full_name method of the user model."""
    assert (
        jobseeker_user.get_full_name()
        == f"{jobseeker_user.first_name} {jobseeker_user.last_name}"
    )


@pytest.mark.django_db
def test_user_string_representation(jobseeker_user):
    """Test the string representation of the user model."""
    assert (
        str(jobseeker_user) == f"{jobseeker_user.first_name} {jobseeker_user.last_name}"
    )  # Should return 'Test User'


# Test user factory
@pytest.mark.django_db
def test_user_factory():
    """Test creating a user using factory_boy."""
    user = UserFactory.create()
    assert user.email == "factoryuser@example.com"
    assert user.first_name == "Factory"
    assert user.last_name == "User"
    assert user.role == "jobseeker"
