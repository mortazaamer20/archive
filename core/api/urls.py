from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ArchiveDocumentViewSet,
    DepartmentViewSet,
    ExternalPartyViewSet,
    KeywordViewSet,
)

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="departments")
router.register(r"external-parties", ExternalPartyViewSet, basename="external-parties")
router.register(r"keywords", KeywordViewSet, basename="keywords")
router.register(r"documents", ArchiveDocumentViewSet, basename="documents")

urlpatterns = [
    path("", include(router.urls)),
]