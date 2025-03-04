import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class JobType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


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
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"


class JobPosting(models.Model):
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey(
        User, related_name="job_postings", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    skills_required = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    expiration_date = models.DateTimeField()
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["job_id"])]

    def __str__(self):
        return self.title
