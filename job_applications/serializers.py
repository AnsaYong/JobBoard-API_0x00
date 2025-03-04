from rest_framework import serializers
from .models import JobApplication, JobApplicationStatus, JobApplicationStatusHistory


class JobApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplicationStatus
        fields = ["status_id", "status_code", "description"]


class JobApplicationSerializer(serializers.ModelSerializer):
    job_id = serializers.StringRelatedField()
    job_seeker_id = serializers.StringRelatedField()
    status = JobApplicationStatusSerializer()

    class Meta:
        model = JobApplication
        fields = [
            "job_application_id",
            "job_id",
            "job_seeker_id",
            "resume_url",
            "cover_letter_url",
            "status",
            "applied_at",
            "updated_at",
        ]


class JobApplicationStatusHistorySerializer(serializers.ModelSerializer):
    status = JobApplicationStatusSerializer()
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = JobApplicationStatusHistory
        fields = [
            "status_hist_id",
            "job_application_id",
            "status",
            "changed_at",
            "changed_by",
        ]
