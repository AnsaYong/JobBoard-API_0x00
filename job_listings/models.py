import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Industry"
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.name


class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Job Location"
        verbose_name_plural = "Job Locations"

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    """
    Represents a job posting on the job board.

    **Fields:**
    - `job_id`: A unique identifier for each job posting (UUID).
    - `employer`: The employer creating the job posting, related to the `User` model (ForeignKey).
    - `title`: The title of the job posting (max length: 255 characters).
    - `description`: A detailed description of the job (TextField).
    - `job_type`: The type of job (e.g., full-time, part-time), related to the `JobType` model (ForeignKey).
    - `location`: The job location, related to the `Location` model (ForeignKey).
    - `industry`: The industry under which the job falls, related to the `Industry` model (ForeignKey).
    - `skills_required`: A list of skills required for the job (TextField).
    - `salary_range`: The salary range for the position (max length: 100 characters, optional).
    - `expiration_date`: The date and time when the job posting expires (DateTimeField).
    - `posted_at`: The date and time when the job posting was created (auto-generated).
    - `updated_at`: The date and time when the job posting was last updated (auto-generated).

    **Meta Information:**
    - `verbose_name`: "Job Posting"
    - `verbose_name_plural`: "Job Postings"
    - `indexes`: Adds an index on `job_id` for faster query performance.

    **Example:**
    ```json
    {
        "job_id": "UUID",
        "employer": "User ID",
        "title": "Software Engineer",
        "description": "We are looking for a Software Engineer with experience in Python.",
        "job_type": "Full-Time",
        "location": "Remote",
        "industry": "Technology",
        "skills_required": "Python, Django, REST APIs",
        "salary_range": "USD 80,000 - 100,000",
        "expiration_date": "2025-12-31T23:59:59Z",
        "posted_at": "2025-03-04T08:00:00Z",
        "updated_at": "2025-03-04T08:00:00Z"
    }
    ```

    **Relationships:**
    - `employer` is a ForeignKey to the `User` model, linking the job to the employer's profile.
    - `job_type` is a ForeignKey to the `JobType` model, specifying the type of job.
    - `location` is a ForeignKey to the `Location` model, indicating the job's location.
    - `industry` is a ForeignKey to the `Industry` model, representing the industry category of the job.

    """

    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey(
        User, related_name="job_postings", on_delete=models.CASCADE, db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    job_type = models.CharField(
        max_length=50,
        choices=(
            ("part-time", "Part-time"),
            ("full-time", "Full-time"),
            ("remote", "Remote"),
        ),
        null=False,
        blank=False,
        db_index=True,
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_index=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, db_index=True)
    skills_required = models.ManyToManyField(
        Skill, db_index=True, related_name="job_postings"
    )
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    expiration_date = models.DateTimeField(db_index=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Posting"
        verbose_name_plural = "Job Postings"
        ordering = ["-posted_at", "location", "industry"]
        indexes = [
            models.Index(fields=["job_id"]),
            models.Index(fields=["title"]),
            models.Index(fields=["job_type"]),
            models.Index(fields=["expiration_date"]),
        ]

    def __str__(self):
        """Returns the title of the job posting as string representation."""
        return self.title
