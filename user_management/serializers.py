from rest_framework import serializers
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from validators import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Methods:
        - validate: Check if the passwords match.
        - create: Create a new user with the hashed password.
    """

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
        """Check if the passwords match and validate the password format."""
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Validate the password strength
        try:
            validate_password(data["password"])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return data

    def create(self, validated_data):
        """Create a new user with the hashed password."""
        validated_data.pop("password2")
        validated_data["password"] = make_password(
            validated_data["password"]
        )  # Hash the password
        user = User.objects.create(**validated_data)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.

    Methods:
        - validate_email: Check if the email exists in the database.
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if the email exists in the database."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_uuid(self, value):
        """Check if the UUID is valid."""
        try:
            user_id = force_str(urlsafe_base64_decode(value))
            user = User.objects.get(pk=user_id)
        except (ValueError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user or UID.")
        return value

    def validate(self, data):
        """Ensure token is valid for the user."""
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer to change the user's password.

    Methods:
    - validate_old_password: Checks if the old password is correct.
    """

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        """Check if the old password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validate the new password against Django's password policy."""
        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Hides the user's password.

    Methods:
    - validate_role: Checks whether the role provided is valid.
    """

    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
        ]
        read_only_fields = ["user_id", "is_active"]

    def validate_role(self, value):
        """Validate that the role is a valid choice."""
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Invalid role. Choose from: {', '.join(valid_roles)}."
            )
        return value
