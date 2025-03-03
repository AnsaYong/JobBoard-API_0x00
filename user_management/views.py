from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer, RegisterSerializer

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
    permission_classes = [AllowAny]

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

    permission_classes = [AllowAny]

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

    permission_classes = [AllowAny]

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


class UserView(viewsets.ModelViewSet):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    print("UserView")
