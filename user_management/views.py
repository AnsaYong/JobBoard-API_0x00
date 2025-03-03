from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
)
from permissions import IsJobBoardAdmin, IsEmployer, IsJobseeker


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Register API for creating new users.

    This endpoint allows users to register by providing their personal details.
    The user will be created if the data is valid and a success response is returned.

    **Request Body:**
    - `email`: (string) Required. User's email address.
    - `first_name`: (string) Required. User's first name.
    - `last_name`: (string) Required. User's last name.
    - `password`: (string) Required. User's password (will be hashed).

    **Response:**
    - `message`: (string) Success message.
    - `data`: (object) Contains user registration details, including `user_id`, `email`, `first_name`, and `last_name`.

    **Responses:**
    - **201 Created**:
        ```json
        {
            "message": "Successful user registration!",
            "data": {
                "user_id": "uuid",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe"
            }
        }
        ```
    - **400 Bad Request**:
        ```json
        {
            "email": ["This field is required."],
            "password": ["This field is required."]
        }
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Handle the POST request for user registration.

        This method processes the registration request and saves the user data if the serializer is valid.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Successful user registration!",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Login API that returns a JWT token.

    This endpoint authenticates the user and returns a JWT access token and refresh token.
    The user needs to provide a valid email and password for authentication.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle the POST request for user login.

        This method authenticates the user with the provided email and password.
        If successful, JWT tokens are returned; otherwise, an error message is provided.

        **Request Body:**
        - `email`: (string) Required. User's email address.
        - `password`: (string) Required. User's password.

        **Response:**
        - `message`: (string) Success message.
        - `data`: (object) Contains `access_token` and `refresh_token` for authenticated user.

        **Responses:**
        - **200 OK**:
            ```json
            {
                "message": "User authenticated successfully",
                "data": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQwOTk5Njg0LCJpYXQiOjE3NDA5OTYwODQsImp0aSI6ImY3MGQ1ZmY4YzQ0ODQ1Y2VhNTc5ZjM0NGE0MTRmYWZjIiwidXNlcl9pZCI6IjA2ZjJmZThkLTM3ZTItNGVkMi04ZDFjLTQ0NDdjMWVkZmFjYSJ9.fCcIYPdiz_h_LUGJV89OWA5oxFAophp8IQu9MA_mD9c",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQwOTk5Njg0LCJpYXQiOjE3NDA5OTYwODQsImp0aSI6ImY3MGQ1ZmY4YzQ0ODQ1Y2VhNTc5ZjM0NGE0MTRmYWZjIiwidXNlcl9pZCI6IjA2ZjJmZThkLTM3ZTItNGVkMi04ZDFjLTQ0NDdjMWVkZmFjYSJ9.fCcIYPdiz_h_LUGJV89OWA5oxFAophp8IQu9MA_mD9c"
                }
            }
            ```
        - **401 Unauthorized**:
            ```json
            {
                "message": "Invalid email or password",
                "status": "error",
                "code": 401
            }
        """
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)  # Returns access and refresh tokens
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "message": "User authenticated successfully",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Invalid email or password",
                "status": "error",
                "code": status.HTTP_401_UNAUTHORIZED,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    """
    Logout API that blacklists refresh tokens.

    This endpoint invalidates the refresh token by blacklisting it, rendering it unusable for future requests.
    Users must provide their refresh token to log out.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Handle the POST request for logging out.

        This method blacklists the provided refresh token, making it unusable for future requests.

        **Request Body:**
        - `refresh_token`: (string) Required. The refresh token that needs to be blacklisted.

        **Response:**
        - `message`: (string) Logout success message.

        **Responses:**
        - **205 Reset Content**:
            ```json
            {
                "message": "Successfully logged out"
            }
            ```
        - **400 Bad Request**:
            ```json
            {
                "error": "Invalid token"
            }
        """
        try:
            refresh_token = request.data.get("refresh_token")  # Get the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Request a password reset.

    This endpoint allows users to request a password reset link by providing their email.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle the POST request for password reset.

        This method sends a password reset link to the user's email if the email exists in the database.

        **Request Body:**
        - `email`: (string) Required. The registered email address.

        **Responses:**
        - **200 OK**: If the email exists, a reset link is sent.
        - **400 Bad Request**: If email is missing or invalid.

        **Example Success Response:**
        ```json
        {
            "message": "Password reset link sent to your email."
        }
        ```
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"https://frontend.com/reset-password/{uid}/{token}/"

            # Send email (prints to console in development)
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_link}",
                from_email="noreply@yourdomain.com",
                recipient_list=[user.email],
            )

        except User.DoesNotExist:
            pass  # To prevent email enumeration

        return Response(
            {"message": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset.

    This endpoint allows users to reset their password by providing a valid token.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        This method resets the user's password if the token is valid.

        **Request Body:**
        - `uid`: (string) Required. Encoded user ID from the password reset link.
        - `token`: (string) Required. Password reset token.
        - `new_password`: (string) Required. The new password.

        **Responses:**
        - **200 OK**: Password reset successful.
        - **400 Bad Request**: Invalid or expired token.

        **Example Success Response:**
        ```json
        {
            "message": "Password reset successfully."
        }
        ```
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Invalid or expired token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"message": "Password reset successfully."}, status=status.HTTP_200_OK
            )

        except (User.DoesNotExist, ValueError):
            return Response(
                {"error": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordChangeView(generics.UpdateAPIView):
    """
    Change password (Authenticated users only).

    This endpoint allows logged-in users to change their password by providing the old password.

    **Request Body:**
    - `old_password`: (string) Required. The user's current password.
    - `new_password`: (string) Required. The new password.

    **Responses:**
    - **200 OK**: Password changed successfully.
    - **400 Bad Request**: If the old password is incorrect.

    **Example Success Response:**
    ```json
    {
        "message": "Password changed successfully."
    }
    ```
    """

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires based on the action.

        This method dynamically sets the permissions for the view based on the action being performed:
        - `list`, `retrieve`, `update`, `partial_update`: Allowed for `IsJobBoardAdmin`, `IsEmployer`, `IsJobseeker`.
        - `create`, `destroy`: Restricted to `IsJobBoardAdmin`.

        **Returns:**
        - A list of permission classes that are applied to the current action.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsJobBoardAdmin | IsEmployer | IsJobseeker]
        elif self.action == "create":
            permission_classes = [IsJobBoardAdmin]
        elif self.action == "destroy":
            permission_classes = [IsJobBoardAdmin]
        else:
            permission_classes = [IsJobBoardAdmin | IsEmployer | IsJobseeker]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Refines the queryset based on the authenticated user's role.

        This method retrieves the users in the system. Admins and superusers can view all users,
        while regular users can only view their own information.

        **Returns:**
        - A queryset of `User` objects filtered based on the user's role.
        """
        user = self.request.user

        if user.role in ["admin", "superuser"]:
            return User.objects.all()
        return User.objects.filter(
            user_id=user.user_id
        )  # Regular users can only see their own info

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        """
        Deactivate the authenticated user's account.

        This endpoint allows users to deactivate their account by setting the 'is_active' field to False.
        Only the authenticated user can deactivate their own account.

        **Responses:**
        - **200 OK**: Account deactivated successfully.
        - **400 Bad Request**: If an error occurs during deactivation.
        - **403 Forbidden**: If the user attempts to deactivate another user's account.

        **Example Success Response:**
        ```json
        {
            "message": "Your account has been deactivated successfully."
        }
        ```

        **Example Error Response:**
        ```json
        {
            "error": "You cannot deactivate another user's account."
        }
        ```
        """
        user = self.get_object()  # User instance based on the URL parameter (pk)

        if user != request.user:
            return Response(
                {"error": "You cannot deactivate another user's account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Deactivate the user's account
        try:
            user.is_active = False
            user.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Your account has been deactivated successfully."},
            status=status.HTTP_200_OK,
        )
