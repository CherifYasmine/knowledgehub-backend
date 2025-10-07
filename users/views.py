from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with user info."""

    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        operation_id="auth_login",
        summary="Login user",
        description="Authenticate user and return JWT tokens with user info",
        responses={
            200: OpenApiResponse(description="Login successful"),
            401: OpenApiResponse(description="Invalid credentials"),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="auth_register",
        summary="Register new user",
        description="Create a new user account",
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Validation errors"),
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            # Generate tokens for the new user
            user = User.objects.get(username=response.data["username"])
            refresh = RefreshToken.for_user(user)

            response.data.update(
                {
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    "message": "User registered successfully",
                }
            )
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "PATCH" or self.request.method == "PUT":
            return UserUpdateSerializer
        return UserSerializer

    @extend_schema(
        operation_id="user_profile_get",
        summary="Get user profile",
        description="Retrieve current user's profile information",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        operation_id="user_profile_update",
        summary="Update user profile",
        description="Update current user's profile information",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    operation_id="auth_change_password",
    summary="Change password",
    description="Change current user's password",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: OpenApiResponse(description="Validation errors"),
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password endpoint."""
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="auth_logout",
    summary="Logout user",
    description="Logout user by blacklisting refresh token",
    responses={
        200: OpenApiResponse(description="Logged out successfully"),
        400: OpenApiResponse(description="Invalid token"),
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """Logout user by blacklisting refresh token."""
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
    except Exception:
        return Response(
            {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
        )
