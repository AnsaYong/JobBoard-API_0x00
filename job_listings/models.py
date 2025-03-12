import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()


class Industry(models.Model):
    """
    Model to represent an industry sector.

    Attributes:
        name (str): The name of the industry (e.g., 'Tech', 'Healthcare').
        created_at (datetime): The date and time when the industry was created.

    Methods:
        __str__: Return the string representation of the Industry (name).
    """

    industry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Industry"
        verbose_name_plural = "Industries"
        indexes = [
            models.Index(fields=["name"]),
        ]
        ordering = ["name"]

    def __str__(self):
        """Return the name of the industry as string representation."""
        return self.name


class Location(models.Model):
    """
    Model to represent a geographical location.

    Attributes:
        city (str): The name of the city.
        postal_code (str): The postal code of the location.
        state_or_province (str): The state or province of the location.
        country (str): The name of the country.

    Methods:
        __str__: Return the string representation of the Location, which is a combination of city and country.
    """

    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    state_or_province = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Job Location"
        verbose_name_plural = "Job Locations"
        indexes = [
            models.Index(
                fields=["city", "country", "state_or_province", "postal_code"]
            ),
        ]
        ordering = ["city", "country"]

    def __str__(self):
        """Return the city and country as string representation."""
        return f"{self.city}, {self.country}"


class Skill(models.Model):
    """
    Model to represent a skill required for a job.
    Makes skill searching/filtering much more efficient

    Attributes:
        skill_id (UUID): A unique identifier for the skill.
        name (str): The name of the skill.

    """

    skill_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        indexes = [
            models.Index(fields=["name"]),
        ]
        ordering = ["name"]

    def __str__(self):
        """Return the name of the skill as string representation."""
        return f"{self.name}"


class JobType(models.TextChoices):
    """Choices for the type of job."""

    PART_TIME = "part-time", "Part-time"
    FULL_TIME = "full-time", "Full-time"
    CONTRACT = "contract", "Contract"
    INTERNSHIP = "internship", "Internship"
    REMOTE = "remote", "Remote"
    FREELANCE = "freelance", "Freelance"
    TEMPORARY = "temporary", "Temporary"
    VOLUNTEER = "volunteer", "Volunteer"


class JobPosting(models.Model):
    """
    Represents a job posting on the job board.

    **Fields:**
    - `job_id`: A unique identifier for each job posting (UUID).
    - `employer`: Employer creating the job. Accidental `User` deletion is prevented by models.PROTECT.
    - `company`: The company offering the job (max length: 255 characters).
    - `title`: The title of the job posting (max length: 255 characters).
    - `slug`: A slug field for SEO-friendly job posting urls.
    - `description`: A detailed description of the job (TextField).
    - `job_type`: The type of job (str). Uses Enum for readability and validation.
    - `location`: The job location, related to the `Location` model (ForeignKey).
    - `industry`: The industry under which the job falls, related to the `Industry` model (ForeignKey).
    - `skills_required`: The skills required for the job, related to the `Skill` model (ManyToManyField).
    - `salary_min`: The minimum salary for the job (DecimalField).
    - `salary_max`: The maximum salary for the job (DecimalField).
    - `currency`: The currency in which the salary is paid (default: ZAR).
    - `is_active`: A boolean field. If False, the job posting is hidden from the job board.
    - `expiration_date`: The date and time when the job posting expires (DateTimeField).
    - `posted_at`: The date and time when the job posting was created (auto-generated).
    - `updated_at`: The date and time when the job posting was last updated (auto-generated).

    **Meta Information:**
    - `verbose_name`: "Job Posting"
    - `verbose_name_plural`: "Job Postings"
    - `indexes`: Adds an index on `job_id` for faster query performance.

    **Methods:**
    - `save`: Override the save method to create a unique slug for each job posting.
    - `__str__`: Returns the title of the job posting as a string representation.

    """

    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey(
        User, related_name="job_postings", on_delete=models.PROTECT, db_index=True
    )
    company = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    job_type = models.CharField(
        max_length=50, choices=JobType.choices, null=False, blank=False, db_index=True
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )
    industry = models.ForeignKey(
        Industry, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )
    skills_required = models.ManyToManyField(
        Skill, related_name="job_postings", blank=True, db_index=True
    )
    salary_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    salary_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=10, default="ZAR")
    is_active = models.BooleanField(default=True, db_index=True)
    expiration_date = models.DateTimeField(db_index=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Posting"
        verbose_name_plural = "Job Postings"
        ordering = ["expiration_date", "-posted_at"]
        indexes = [
            models.Index(fields=["job_id"]),
            models.Index(fields=["title"]),
            models.Index(fields=["job_type"]),
            models.Index(fields=["expiration_date"]),
            models.Index(fields=["industry"]),
        ]

    def save(self, *args, **kwargs):
        """
        Override the save method to create a unique slug for each job posting.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def delete_job(self):
        """
        Soft delete the job posting by setting the `is_active` field to False.
        """
        self.is_active = False
        self.save()

    def __str__(self):
        """
        Returns the title of the job posting as string representation.
        """
        return f"{self.title} - {self.company}"
