from django.db.models import Count
from django.utils import timezone

from .models import ArchiveDocument, Department, ExternalParty, Keyword


def dashboard_callback(request, context):
    today = timezone.localdate()

    context.update(
        {
            "total_documents": ArchiveDocument.objects.count(),
            "today_documents": ArchiveDocument.objects.filter(
                registered_at__date=today
            ).count(),
            "internal_documents": ArchiveDocument.objects.filter(
                document_kind__in=["internal_outgoing", "internal_incoming"]
            ).count(),
            "external_documents": ArchiveDocument.objects.filter(
                document_kind__in=["external_outgoing", "external_incoming"]
            ).count(),
            "departments_count": Department.objects.count(),
            "external_parties_count": ExternalParty.objects.count(),
            "keywords_count": Keyword.objects.count(),
            "latest_documents": ArchiveDocument.objects.select_related(
                "source_department",
                "destination_department",
                "source_external_party",
                "destination_external_party",
            ).order_by("-registered_at")[:8],
        }
    )
    return context