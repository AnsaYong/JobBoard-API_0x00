from rest_framework import serializers
from .models import Industry, Location, Skill, JobPosting


class IndustrySerializer(serializers.ModelSerializer):
    """
    Serializer for the Industry model.
    """

    class Meta:
        model = Industry
        fields = ["industry_id", "name"]


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.
    """

    class Meta:
        model = Location
        fields = ["location_id", "city", "postal_code", "state_or_province", "country"]


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Skill model.
    """

    class Meta:
        model = Skill
        fields = ["skill_id", "name"]


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobPosting model with dynamic creation of related fields.

    Fields:
        - employer (PrimaryKeyRelatedField): Auto-assigned from request user.
        - location (LocationSerializer): Allows nested location creation.
        - industry (IndustrySerializer): Allows nested industry creation.
        - skills_required (SkillSerializer): Many-to-many relationship.
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
            "company",
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
        """Create a new job posting while ensuring related objects are properly handled."""
        location_data = validated_data.pop("location")
        industry_data = validated_data.pop("industry")
        skills_data = validated_data.pop("skills_required", [])

        # Get or create location
        location, _ = Location.objects.get_or_create(
            city=location_data["city"],
            state_or_province=location_data.get("state_or_province", ""),
            country=location_data["country"],
        )

        # Get or create industry
        industry, _ = Industry.objects.get_or_create(name=industry_data["name"])

        # Create job posting
        job_posting = JobPosting.objects.create(
            location=location, industry=industry, **validated_data
        )

        # Add skills (efficiently handling get_or_create)
        skill_instances = []
        for skill_data in skills_data:
            skill, _ = Skill.objects.get_or_create(name=skill_data["name"])
            skill_instances.append(skill)
        job_posting.skills_required.set(skill_instances)

        return job_posting
