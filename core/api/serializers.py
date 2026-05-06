from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import (
    ArchiveDocument,
    ArchiveDocumentAttachment,
    Department,
    ExternalParty,
    Keyword,
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code", "is_active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ExternalPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalParty
        fields = [
            "id",
            "name",
            "code",
            "address",
            "phone",
            "email",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["id", "name", "created_at"]
        read_only_fields = ["created_at"]


class ArchiveDocumentAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ArchiveDocumentAttachment
        fields = [
            "id",
            "document",
            "title",
            "file",
            "file_url",
            "original_name",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = ["original_name", "uploaded_by", "uploaded_at", "file_url"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if not obj.file:
            return None
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["uploaded_by"] = request.user
        return super().create(validated_data)


class ArchiveDocumentSerializer(serializers.ModelSerializer):
    source_department_detail = DepartmentSerializer(source="source_department", read_only=True)
    destination_department_detail = DepartmentSerializer(source="destination_department", read_only=True)
    source_external_party_detail = ExternalPartySerializer(source="source_external_party", read_only=True)
    destination_external_party_detail = ExternalPartySerializer(source="destination_external_party", read_only=True)

    keywords_detail = KeywordSerializer(source="keywords", many=True, read_only=True)
    attachments = ArchiveDocumentAttachmentSerializer(many=True, read_only=True)

    keyword_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Keyword.objects.all(),
        write_only=True,
        required=False,
    )

    main_file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ArchiveDocument
        fields = [
            "id",
            "document_kind",
            "document_number",
            "document_date",
            "subject",
            "content",
            "source_department",
            "destination_department",
            "source_external_party",
            "destination_external_party",
            "file_number",
            "storage_number",
            "archive_box_number",
            "archive_folder_number",
            "archive_location_note",
            "pages_count",
            "copies_count",
            "confidentiality",
            "status",
            "received_at",
            "registered_at",
            "updated_at",
            "created_by",
            "updated_by",
            "main_file",
            "main_file_url",
            "file_original_name",
            "file_checksum",
            "notes",
            "keywords_detail",
            "keyword_ids",
            "attachments",
            "source_department_detail",
            "destination_department_detail",
            "source_external_party_detail",
            "destination_external_party_detail",
        ]
        read_only_fields = [
            "registered_at",
            "updated_at",
            "created_by",
            "updated_by",
            "file_original_name",
            "file_checksum",
            "main_file_url",
        ]

    def get_main_file_url(self, obj):
        request = self.context.get("request")
        if not obj.main_file:
            return None
        if request:
            return request.build_absolute_uri(obj.main_file.url)
        return obj.main_file.url

    def validate(self, attrs):
        instance = self.instance or ArchiveDocument()

        for field, value in attrs.items():
            setattr(instance, field, value)

        keyword_ids = attrs.get("keyword_ids", None)

        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        keyword_ids = validated_data.pop("keyword_ids", [])
        request = self.context.get("request")

        if request and request.user and request.user.is_authenticated:
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user

        document = ArchiveDocument.objects.create(**validated_data)

        if keyword_ids:
            document.keywords.set(keyword_ids)

        return document

    @transaction.atomic
    def update(self, instance, validated_data):
        keyword_ids = validated_data.pop("keyword_ids", None)
        request = self.context.get("request")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if request and request.user and request.user.is_authenticated:
            instance.updated_by = request.user

        instance.full_clean()
        instance.save()

        if keyword_ids is not None:
            instance.keywords.set(keyword_ids)

        return instance