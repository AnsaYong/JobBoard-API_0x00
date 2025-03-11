import factory
from job_listings.models import Industry, Location, Skill, JobPosting


class IndustryFactory(factory.django.DjangoModelFactory):
    """Factory for creating Industry instances."""

    class Meta:
        model = Industry
        skip_postgeneration_save = True

    name = factory.Faker("word")


class LocationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Location instances."""

    class Meta:
        model = Location
        skip_postgeneration_save = True

    city = factory.Faker("city")
    country = factory.Faker("country")
    state_or_province = factory.Faker("state")
    postal_code = factory.Faker("zipcode")


class SkillFactory(factory.django.DjangoModelFactory):
    """Factory for creating Skill instances."""

    class Meta:
        model = Skill
        skip_postgeneration_save = True

    name = factory.Faker("word")


class JobListingFactory(factory.django.DjangoModelFactory):
    """Factory for creating a JobPosting instance."""

    class Meta:
        model = JobPosting
        skip_postgeneration_save = True

    employer = factory.SubFactory("user_management.tests.factories.UserFactory")
    company = factory.Faker("company")
    title = factory.Faker("job")
    description = factory.Faker("text")
    job_type = "full-time"
    location = factory.SubFactory(LocationFactory)
    industry = factory.SubFactory(IndustryFactory)
    skills_required = factory.RelatedFactoryList(SkillFactory, "job_postings", size=3)
    expiration_date = factory.Faker("date_this_year")
