"""Factory definitionsf for user_management app."""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    """A factory for the user model using factory_boy."""

    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"factoryuser{n}@example.com")  # Unique emails
    first_name = "Factory"
    last_name = "User"
    role = "jobseeker"
    password = factory.PostGenerationMethodCall("set_password", "password123")
