from rest_framework import serializers
from .models import JobPosting, Industry, Location


class IndustrySerializer(serializers.ModelSerializer):
    """
    Serializer for the Industry model.

    Serializes data for creating and updating industries, as well as reading industry information.

    Attributes:
        name (str): The name of the industry.

    Methods:
        create: Create a new industry.
        update: Update an existing industry.
    """

    class Meta:
        model = Industry
        fields = ["industry_id", "name"]


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.

    Serializes data for creating and updating locations, as well as reading location information.

    Attributes:
        city (str): The city of the location.
        country (str): The country of the location.

    Methods:
        create: Create a new location.
        update: Update an existing location.
    """

    class Meta:
        model = Location
        fields = ["location_id", "city", "country"]


class JobPostingSerializer(serializers.ModelSerializer):
    industry = serializers.PrimaryKeyRelatedField(queryset=Industry.objects.all())
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

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
        read_only_fields = ["job_id", "employer", "posted_at", "updated_at"]

    def validate(self, attrs):
        print("In Serializer validate method")
        location_data = attrs.get("location", None)
        industry_data = attrs.get("industry", None)

        if not location_data:
            raise serializers.ValidationError("Location is required")

        if not industry_data:
            raise serializers.ValidationError("Industry is required")

        return attrs

    def create(self, validated_data):
        print("In Serializer create method")
        location_data = validated_data.get("location", None)
        industry_data = validated_data.get("industry", None)

        # If location is a string (user-typed), create or fetch the Location
        if isinstance(location_data, str):
            location_data = Location.objects.get_or_create(city=location_data)[0]

        # If industry is a string (user-typed), create or fetch the Industry
        if isinstance(industry_data, str):
            industry_data = Industry.objects.get_or_create(name=industry_data)[0]

        validated_data["location"] = location_data
        validated_data["industry"] = industry_data

        job_posting = JobPosting.objects.create(**validated_data)
        return job_posting

    def update(self, instance, validated_data):
        location_data = validated_data.get("location", instance.location)
        industry_data = validated_data.get("industry", instance.industry)

        if isinstance(location_data, str):
            location_data = Location.objects.get_or_create(city=location_data)[0]

        if isinstance(industry_data, str):
            industry_data = Industry.objects.get_or_create(name=industry_data)[0]

        instance.location = location_data
        instance.industry = industry_data

        instance.save()
        return instance
