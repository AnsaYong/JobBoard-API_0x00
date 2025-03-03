from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        validated_data["password"] = make_password(
            validated_data["password"]
        )  # Hash the password
        user = User.objects.create(**validated_data)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        """Check if the old password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email", "username", "first_name", "last_name", "role"]
        read_only_fields = ["user_id"]
