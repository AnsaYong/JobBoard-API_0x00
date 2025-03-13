import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from job_listings.models import JobPosting, Industry, Location, Skill, JobType

User = get_user_model()


class Command(BaseCommand):
    help = "Create 100 job postings with realistic data"

    def handle(self, *args, **kwargs):

        # Clear existing job postings
        self.stdout.write(self.style.WARNING("Clearing existing job posting data..."))
        JobPosting.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Cleared existing job postings."))

        fake = Faker()

        # Get existing employers
        employers = User.objects.filter(role="employer")
        industries = Industry.objects.all()
        locations = Location.objects.all()
        skills = Skill.objects.all()

        # Check if required data exists
        if not employers or not industries or not locations or not skills:
            self.stdout.write(
                self.style.ERROR(
                    "Missing necessary data (employers, industries, locations, skills)"
                )
            )
            return

        job_types = [
            JobType.PART_TIME,
            JobType.FULL_TIME,
            JobType.CONTRACT,
            JobType.INTERNSHIP,
            JobType.REMOTE,
        ]

        # Create 100 job postings
        for _ in range(100):
            employer = random.choice(employers)
            industry = random.choice(industries)
            location = random.choice(locations)
            skill_count = random.randint(1, 5)  # Jobs can require 1-5 skills
            required_skills = random.sample(list(skills), skill_count)

            # Random job details
            job_title = fake.job()
            company_name = fake.company()
            job_description = fake.paragraph(nb_sentences=5)
            job_type = random.choice(job_types)
            salary_min = random.randint(25000, 100000)
            salary_max = salary_min + random.randint(10000, 40000)
            expiration_date = timezone.now() + timezone.timedelta(
                days=random.randint(30, 90)
            )  # Random expiration in 30-90 days

            # Create job posting
            job_posting = JobPosting.objects.create(
                employer=employer,
                company=company_name,
                title=job_title,
                description=job_description,
                job_type=job_type,
                location=location,
                industry=industry,
                salary_min=salary_min,
                salary_max=salary_max,
                expiration_date=expiration_date,
            )

            # Add skills to job posting
            job_posting.skills_required.set(required_skills)
            job_posting.save()

        self.stdout.write(self.style.SUCCESS("Successfully created 100 job postings."))
