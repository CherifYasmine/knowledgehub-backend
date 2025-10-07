from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "users"

urlpatterns = [
    # Authentication endpoints
    path(
        "auth/login/", views.CustomTokenObtainPairView.as_view(), name="login"
    ),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "auth/register/", views.UserRegistrationView.as_view(), name="register"
    ),
    path("auth/logout/", views.logout, name="logout"),
    path(
        "auth/change-password/", views.change_password, name="change_password"
    ),
    # User profile endpoints
    path("profile/", views.UserProfileView.as_view(), name="profile"),
]
