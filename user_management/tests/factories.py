"""Factory definitionsf for user_management app."""

from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    """A factory for the user model using factory_boy."""

    class Meta:
        model = get_user_model()

    email = "factoryuser@example.com"
    first_name = "Factory"
    last_name = "User"
    role = "jobseeker"
    password = "password123"
