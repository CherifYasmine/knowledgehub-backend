from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "comments"

# Create router and register viewsets
router = DefaultRouter()
router.register(r"comments", views.CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
