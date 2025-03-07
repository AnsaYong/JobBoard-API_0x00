from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError


def create_default_industries(sender, **kwargs):
    """
    Create default industries after migrations.
    """
    from job_listings.models import Industry  # Avoid circular imports

    default_industries = [
        {"name": "Technology"},
        {"name": "Healthcare"},
        {"name": "Finance"},
        {"name": "Education"},
        {"name": "Retail"},
        {"name": "Manufacturing"},
        {"name": "Construction"},
        {"name": "Government"},
    ]

    try:
        for industry in default_industries:
            Industry.objects.get_or_create(name=industry["name"])
    except (OperationalError, ProgrammingError):
        # Ignore errors if the database is not ready yet (e.g., first migration)
        pass


def create_default_locations(sender, **kwargs):
    """
    Create default locations after migrations.
    """
    from job_listings.models import Location  # Avoid circular imports

    default_locations = [
        {"city": "New York", "country": "USA"},
        {"city": "San Francisco", "country": "USA"},
        {"city": "London", "country": "UK"},
        {"city": "Berlin", "country": "Germany"},
        {"city": "Toronto", "country": "Canada"},
        {"city": "Sydney", "country": "Australia"},
        {"city": "Mumbai", "country": "India"},
        {"city": "Paris", "country": "France"},
    ]

    try:
        for location in default_locations:
            Location.objects.get_or_create(
                city=location["city"],
                country=location["country"],
            )
    except (OperationalError, ProgrammingError):
        # Ignore errors if the database is not ready yet (e.g., first migration)
        pass


def create_default_skills(sender, **kwargs):
    """
    Create default skills after migrations.
    """
    from job_listings.models import Skill  # Avoid circular imports

    default_skills = [
        {"name": "Python"},
        {"name": "JavaScript"},
        {"name": "Java"},
        {"name": "SQL"},
        {"name": "React"},
        {"name": "Node.js"},
        {"name": "AWS"},
        {"name": "Project Management"},
        {"name": "Data Analysis"},
        {"name": "Machine Learning"},
        {"name": "UI/UX Design"},
        {"name": "Team Leadership"},
    ]

    try:
        for skill in default_skills:
            Skill.objects.get_or_create(name=skill["name"])
    except (OperationalError, ProgrammingError):
        # Ignore errors if the database is not ready yet (e.g., first migration)
        pass


class JobListingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "job_listings"

    def ready(self):
        # Connect signals to create default data after migrations
        post_migrate.connect(create_default_industries, sender=self)
        post_migrate.connect(create_default_locations, sender=self)
        post_migrate.connect(create_default_skills, sender=self)
