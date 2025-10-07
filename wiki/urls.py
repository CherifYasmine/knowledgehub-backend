from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "wiki"

# Create router and register viewsets
router = DefaultRouter()
router.register(r"articles", views.ArticleViewSet)
router.register(r"sections", views.SectionViewSet)
router.register(r"revisions", views.RevisionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
