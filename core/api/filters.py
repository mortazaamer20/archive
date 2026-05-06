import django_filters
from django_filters.rest_framework import FilterSet

from .models import ArchiveDocument, Keyword


class ArchiveDocumentFilter(FilterSet):
    document_date_from = django_filters.DateFilter(field_name="document_date", lookup_expr="gte")
    document_date_to = django_filters.DateFilter(field_name="document_date", lookup_expr="lte")

    registered_at_from = django_filters.DateTimeFilter(field_name="registered_at", lookup_expr="gte")
    registered_at_to = django_filters.DateTimeFilter(field_name="registered_at", lookup_expr="lte")

    keyword = django_filters.CharFilter(field_name="keywords__name", lookup_expr="icontains")

    keyword_id = django_filters.ModelChoiceFilter(
        field_name="keywords",
        queryset=Keyword.objects.all(),
    )

    class Meta:
        model = ArchiveDocument
        fields = [
            "document_kind",
            "status",
            "confidentiality",
            "source_department",
            "destination_department",
            "source_external_party",
            "destination_external_party",
            "file_number",
            "storage_number",
            "archive_box_number",
            "archive_folder_number",
        ]