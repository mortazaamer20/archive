from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RelatedDropdownFilter,
    RangeDateFilter,
    RangeDateTimeFilter,
)

from .models import (
    ArchiveDocument,
    ArchiveDocumentAttachment,
    Department,
    ExternalParty,
    Keyword,
)


@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ["name", "code", "is_active"]
    search_fields = ["name", "code"]
    list_filter = [("is_active", ChoicesDropdownFilter)]
    ordering = ["name"]
    compressed_fields = True
    warn_unsaved_form = True


@admin.register(ExternalParty)
class ExternalPartyAdmin(ModelAdmin):
    list_display = ["name", "code", "is_active", "phone", "email"]
    search_fields = ["name", "code", "phone", "email"]
    list_filter = [("is_active", ChoicesDropdownFilter)]
    ordering = ["name"]
    compressed_fields = True
    warn_unsaved_form = True


@admin.register(Keyword)
class KeywordAdmin(ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    ordering = ["name"]
    compressed_fields = True


class ArchiveDocumentAttachmentInline(admin.TabularInline):
    model = ArchiveDocumentAttachment
    extra = 0


@admin.register(ArchiveDocument)
class ArchiveDocumentAdmin(ModelAdmin):
    list_display = [
        "document_number",
        "subject",
        "document_kind_badge",
        "document_date",
        "status",
        "storage_number",
        "file_number",
        "registered_at",
    ]
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
    list_filter = [
        ("document_kind", ChoicesDropdownFilter),
        ("status", ChoicesDropdownFilter),
        ("confidentiality", ChoicesDropdownFilter),
        ("document_date", RangeDateFilter),
        ("registered_at", RangeDateTimeFilter),
        ("source_department", RelatedDropdownFilter),
        ("destination_department", RelatedDropdownFilter),
    ]
    ordering = ["-document_date", "-registered_at"]
    filter_horizontal = ["keywords"]
    inlines = [ArchiveDocumentAttachmentInline]

    compressed_fields = True
    warn_unsaved_form = True
    show_add_link = True

    readonly_fields = [
        "file_original_name",
        "file_checksum",
        "registered_at",
        "updated_at",
    ]

    fieldsets = (
        ("بيانات الكتاب", {
            "fields": (
                "document_kind",
                "document_number",
                "document_date",
                "subject",
                "content",
            ),
            "classes": ("tab",),
        }),
        ("جهات الربط", {
            "fields": (
                "source_department",
                "destination_department",
                "source_external_party",
                "destination_external_party",
            ),
            "classes": ("tab",),
        }),
        ("الخزن والأرشفة", {
            "fields": (
                "file_number",
                "storage_number",
                "archive_box_number",
                "archive_folder_number",
                "archive_location_note",
            ),
            "classes": ("tab",),
        }),
        ("المعلومات الإضافية", {
            "fields": (
                "pages_count",
                "copies_count",
                "confidentiality",
                "status",
                "received_at",
                "keywords",
                "notes",
            ),
            "classes": ("tab",),
        }),
        ("الملف", {
            "fields": (
                "main_file",
                "file_original_name",
                "file_checksum",
            ),
            "classes": ("tab",),
        }),
        ("التدقيق", {
            "fields": (
                "created_by",
                "updated_by",
                "registered_at",
                "updated_at",
            ),
            "classes": ("tab",),
        }),
    )

    def document_kind_badge(self, obj):
        color = {
            "internal_outgoing": "bg-blue-100 text-blue-800",
            "internal_incoming": "bg-green-100 text-green-800",
            "external_outgoing": "bg-purple-100 text-purple-800",
            "external_incoming": "bg-orange-100 text-orange-800",
        }.get(obj.document_kind, "bg-gray-100 text-gray-800")

        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold {}">{}</span>',
            color,
            obj.get_document_kind_display(),
        )

    document_kind_badge.short_description = "نوع الكتاب"