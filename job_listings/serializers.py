from rest_framework import serializers
from .models import JobPosting, Industry, Location


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ["id", "name"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "city", "state", "country"]


class JobPostingSerializer(serializers.ModelSerializer):
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

    def perform_create(self, validated_data):
        industry_data = validated_data.pop("industry")
        location_data = validated_data.pop("location")

        industry = Industry.objects.create(**industry_data)
        location = Location.objects.create(**location_data)

        job_posting = JobPosting.objects.create(
            industry=industry, location=location, **validated_data
        )
        return job_posting
