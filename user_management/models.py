from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class CustomUserManager(BaseUserManager):
    """Custom manager for User model with email authentication.
    Overrides the create_user and create_superuser methods ensuring the `username` field is not required.
    """

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for the job board system.

    This model extends Django's AbstractUser and uses `email` as the primary authentication field.
    It includes role-based access control and timestamps for tracking user creation and updates.

    Fields:
        - `user_id (UUIDField)`: Primary key using a UUID for uniqueness across distributed systems.
        - `email (EmailField)`: Unique email address (used for authentication).
        - `first_name (CharField)`: User's first name (required).
        - `last_name (CharField)`: User's last name (required).
        - `role (CharField)`: Defines user roles (admin, jobseeker, employer).
        - `created_at (DateTimeField)`: Timestamp when the user was created.
        - `updated_at (DateTimeField)`: Timestamp when the user profile was last updated.

    Authentication:
        - `username = None`: Disables username-based authentication.
        - `USERNAME_FIELD = "email"`: Uses email for authentication.
        - `REQUIRED_FIELDS = ["first_name", "last_name"]`: Required fields for user creation.

    Meta:
        - `ordering = ["-created_at"]`: Orders users by most recently created first.
        - `constraints`: Ensures unique email addresses at the database level.

    Methods:
        - `__str__()`: Returns a user-friendly string representation.
    """

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False, blank=False, db_index=True)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    role = models.CharField(
        max_length=50,
        choices=(
            ("admin", "Admin"),
            ("jobseeker", "Jobseeker"),
            ("employer", "Employer"),
        ),
        null=False,
        blank=False,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Configure the User model to use the email field for authentication
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email_constraint")
        ]

    def __str__(self):
        """Returns user's full name as string representation."""
        return f"{self.first_name} {self.last_name}"
