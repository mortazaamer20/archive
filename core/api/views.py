from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ArchiveDocumentFilter
from .models import ArchiveDocument, ArchiveDocumentAttachment, Department, ExternalParty, Keyword
from .serializers import (
    ArchiveDocumentAttachmentSerializer,
    ArchiveDocumentSerializer,
    DepartmentSerializer,
    ExternalPartySerializer,
    KeywordSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]


class ExternalPartyViewSet(viewsets.ModelViewSet):
    queryset = ExternalParty.objects.all()
    serializer_class = ExternalPartySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "code", "address", "phone", "email"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]


class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class ArchiveDocumentViewSet(viewsets.ModelViewSet):
    queryset = (
        ArchiveDocument.objects.select_related(
            "source_department",
            "destination_department",
            "source_external_party",
            "destination_external_party",
            "created_by",
            "updated_by",
        )
        .prefetch_related("keywords", "attachments")
        .all()
    )
    serializer_class = ArchiveDocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ArchiveDocumentFilter
    search_fields = [
        "document_number",
        "subject",
        "content",
        "file_number",
        "storage_number",
        "archive_box_number",
        "archive_folder_number",
        "keywords__name",
    ]
    ordering_fields = ["document_date", "registered_at", "updated_at", "document_number"]
    ordering = ["-document_date", "-registered_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.distinct()

    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
        url_path="attachments",
    )
    def add_attachment(self, request, pk=None):
        document = self.get_object()
        serializer = ArchiveDocumentAttachmentSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save(document=document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="attachments-list")
    def attachments_list(self, request, pk=None):
        document = self.get_object()
        serializer = ArchiveDocumentAttachmentSerializer(
            document.attachments.all(),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)