from rest_framework import serializers
from .models import JobPosting, JobType, Industry, Location


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ["id", "name"]


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ["id", "name"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "city", "state", "country"]


class JobPostingSerializer(serializers.ModelSerializer):
    job_type = JobTypeSerializer()
    industry = IndustrySerializer()
    location = LocationSerializer()

    class Meta:
        model = JobPosting
        fields = [
            "job_id",
            "employer",
            "title",
            "description",
            "job_type",
            "location",
            "industry",
            "skills_required",
            "salary_range",
            "expiration_date",
            "posted_at",
            "updated_at",
        ]

    def create(self, validated_data):
        job_type_data = validated_data.pop("job_type")
        industry_data = validated_data.pop("industry")
        location_data = validated_data.pop("location")

        job_type = JobType.objects.create(**job_type_data)
        industry = Industry.objects.create(**industry_data)
        location = Location.objects.create(**location_data)

        job_posting = JobPosting.objects.create(
            job_type=job_type, industry=industry, location=location, **validated_data
        )
        return job_posting
