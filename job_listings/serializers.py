from rest_framework import serializers
from .models import Industry, Location, Skill, JobPosting


class IndustrySerializer(serializers.ModelSerializer):
    """
    Serializer for the Industry model.

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

    Methods:
        create: Create a new location.
        update: Update an existing location
    """

    class Meta:
        model = Location
        fields = ["location_id", "city", "postal_code", "state_or_province", "country"]


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Skill model.

    Methods:
        create: Create a new skill.
        update: Update an existing skill.
    """

    class Meta:
        model = Skill
        fields = ["skill_id", "name"]


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobPosting model with support for both UUID and string-based
    input for location and industry.

    Attributes:
        - employer (PrimaryKeyRelatedField): The employer of the job posting.
        Auto-assgined from request user
    Nested Serializers:
        - location (LocationSerializer): The location of the job posting.
        - industry (IndustrySerializer): The industry of the job posting.
        - skills_required (SkillSerializer): The skills required. Many-to-many relationship.
    """

    employer = serializers.PrimaryKeyRelatedField(read_only=True)
    location = LocationSerializer()
    industry = IndustrySerializer()
    skills_required = SkillSerializer(many=True)

    class Meta:
        model = JobPosting
        fields = [
            "job_id",
            "employer",
            "title",
            "slug",
            "description",
            "job_type",
            "location",
            "industry",
            "skills_required",
            "salary_min",
            "salary_max",
            "currency",
            "expiration_date",
            "posted_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = [
            "job_id",
            "employer",
            "posted_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create a new job posting with related location and industry"""
        location_data = validated_data.pop("location")
        industry_data = validated_data.pop("industry")
        skills_data = validated_data.pop("skills_required", [])

        # Create or get related objects
        location, _ = Location.objects.get_or_create(**location_data)
        industry, _ = Industry.objects.get_or_create(**industry_data)
        job_posting = JobPosting.objects.create(
            location=location, industry=industry, **validated_data
        )

        # Add skills
        for skill_data in skills_data:
            skill, _ = Skill.objects.get_or_create(**skill_data)
            job_posting.skills_required.add(skill)

        return job_posting
