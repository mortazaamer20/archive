import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

ALLOWED_ARCHIVE_EXTENSIONS = [
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "tif",
    "tiff",
    "bmp",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
    "txt",
    "rtf",
    "odt",
    "ods",
]


def validate_file_size(file_obj):
    if file_obj.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"حجم الملف يجب ألا يتجاوز {MAX_UPLOAD_SIZE // (1024 * 1024)} MB."
        )


def archive_upload_to(instance, filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    return f"archive/documents/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{ext}"


def attachment_upload_to(instance, filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    return f"archive/attachments/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{ext}"


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم القسم")
    code = models.CharField(max_length=50, unique=True, verbose_name="رمز القسم")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class ExternalParty(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم الجهة الخارجية")
    code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="رمز الجهة الخارجية",
    )
    address = models.CharField(max_length=255, blank=True, verbose_name="العنوان")
    phone = models.CharField(max_length=50, blank=True, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "جهة خارجية"
        verbose_name_plural = "الجهات الخارجية"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="الكلمة المفتاحية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "كلمة مفتاحية"
        verbose_name_plural = "الكلمات المفتاحية"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class ArchiveDocument(models.Model):
    class Kind(models.TextChoices):
        INTERNAL_OUTGOING = "internal_outgoing", "صادر داخلي"
        INTERNAL_INCOMING = "internal_incoming", "وارد داخلي"
        EXTERNAL_OUTGOING = "external_outgoing", "صادر خارجي"
        EXTERNAL_INCOMING = "external_incoming", "وارد خارجي"

    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        REGISTERED = "registered", "مُسجل"
        ARCHIVED = "archived", "مؤرشف"
        CLOSED = "closed", "مغلق"

    class Confidentiality(models.TextChoices):
        NORMAL = "normal", "عادي"
        INTERNAL = "internal", "داخلي"
        CONFIDENTIAL = "confidential", "سري"
        TOP_SECRET = "top_secret", "سري جداً"

    document_kind = models.CharField(
        max_length=32,
        choices=Kind.choices,
        verbose_name="نوع الكتاب",
        db_index=True,
    )

    document_number = models.CharField(
        max_length=100,
        verbose_name="رقم الكتاب",
        db_index=True,
    )
    document_date = models.DateField(
        verbose_name="تاريخ الكتاب",
        db_index=True,
    )

    subject = models.CharField(
        max_length=255,
        verbose_name="موضوع الكتاب",
        db_index=True,
    )
    content = models.TextField(verbose_name="محتوى الكتاب", blank=True)

    source_department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_documents",
        verbose_name="القسم الصادر منه",
    )
    destination_department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="received_documents",
        verbose_name="القسم الوارد إليه",
    )

    source_external_party = models.ForeignKey(
        ExternalParty,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_documents",
        verbose_name="الجهة الخارجية الصادر منها",
    )
    destination_external_party = models.ForeignKey(
        ExternalParty,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="received_documents",
        verbose_name="الجهة الخارجية الوارد إليها",
    )

    file_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="رقم الفايل",
        db_index=True,
    )
    storage_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="رقم الخزن",
        db_index=True,
    )
    archive_box_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="رقم الصندوق",
    )
    archive_folder_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="رقم المجلد",
    )
    archive_location_note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="موقع الحفظ",
    )

    pages_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="عدد الصفحات",
    )
    copies_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="عدد النسخ",
    )

    confidentiality = models.CharField(
        max_length=20,
        choices=Confidentiality.choices,
        default=Confidentiality.NORMAL,
        verbose_name="درجة السرية",
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED,
        verbose_name="الحالة",
        db_index=True,
    )

    received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الاستلام",
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ التسجيل",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_archive_documents",
        verbose_name="أنشأ بواسطة",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_archive_documents",
        verbose_name="عدل بواسطة",
    )

    main_file = models.FileField(
        upload_to=archive_upload_to,
        null=True,
        blank=True,
        verbose_name="الملف الرئيسي",
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_ARCHIVE_EXTENSIONS),
            validate_file_size,
        ],
    )
    file_original_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="اسم الملف الأصلي",
    )
    file_checksum = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="بصمة الملف",
    )

    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        related_name="documents",
        verbose_name="الكلمات المفتاحية",
    )

    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "كتاب مؤرشف"
        verbose_name_plural = "الكتب المؤرشفة"
        ordering = ["-document_date", "-registered_at"]
        indexes = [
            models.Index(fields=["document_number"]),
            models.Index(fields=["document_date"]),
            models.Index(fields=["document_kind"]),
            models.Index(fields=["status"]),
            models.Index(fields=["storage_number"]),
            models.Index(fields=["file_number"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["document_number", "document_date"],
                name="uniq_document_number_document_date",
            ),
        ]

    def __str__(self):
        return f"{self.document_number} - {self.subject}"

    def clean(self):
        errors = {}

        kind = self.document_kind

        if kind == self.Kind.INTERNAL_OUTGOING:
            if not self.source_department:
                errors["source_department"] = "هذا الحقل مطلوب للصادر الداخلي."
            if not self.destination_department:
                errors["destination_department"] = "هذا الحقل مطلوب للصادر الداخلي."

            if self.source_external_party:
                errors["source_external_party"] = "لا يجب تعبئة جهة خارجية في الصادر الداخلي."
            if self.destination_external_party:
                errors["destination_external_party"] = "لا يجب تعبئة جهة خارجية في الصادر الداخلي."

        elif kind == self.Kind.INTERNAL_INCOMING:
            if not self.source_department:
                errors["source_department"] = "هذا الحقل مطلوب للوارد الداخلي."
            if not self.destination_department:
                errors["destination_department"] = "هذا الحقل مطلوب للوارد الداخلي."

            if self.source_external_party:
                errors["source_external_party"] = "لا يجب تعبئة جهة خارجية في الوارد الداخلي."
            if self.destination_external_party:
                errors["destination_external_party"] = "لا يجب تعبئة جهة خارجية في الوارد الداخلي."

        elif kind == self.Kind.EXTERNAL_OUTGOING:
            if not self.source_department:
                errors["source_department"] = "هذا الحقل مطلوب للصادر الخارجي."
            if not self.destination_external_party:
                errors["destination_external_party"] = "هذا الحقل مطلوب للصادر الخارجي."

            if self.destination_department:
                errors["destination_department"] = "لا يجب تعبئة قسم داخلي في الصادر الخارجي."
            if self.source_external_party:
                errors["source_external_party"] = "لا يجب تعبئة جهة خارجية في الصادر الخارجي."

        elif kind == self.Kind.EXTERNAL_INCOMING:
            if not self.source_external_party:
                errors["source_external_party"] = "هذا الحقل مطلوب للوارد الخارجي."
            if not self.destination_department:
                errors["destination_department"] = "هذا الحقل مطلوب للوارد الخارجي."

            if self.source_department:
                errors["source_department"] = "لا يجب تعبئة قسم داخلي في الوارد الخارجي."
            if self.destination_external_party:
                errors["destination_external_party"] = "لا يجب تعبئة جهة خارجية في الوارد الخارجي."

        if self.main_file and not self.file_original_name:
            self.file_original_name = os.path.basename(self.main_file.name)

        if errors:
            raise ValidationError(errors)


class ArchiveDocumentAttachment(models.Model):
    document = models.ForeignKey(
        ArchiveDocument,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="الكتاب",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="عنوان المرفق",
    )
    file = models.FileField(
        upload_to=attachment_upload_to,
        verbose_name="الملف",
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_ARCHIVE_EXTENSIONS),
            validate_file_size,
        ],
    )
    original_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="اسم الملف الأصلي",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="archive_document_attachments",
        verbose_name="رفع بواسطة",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")

    class Meta:
        verbose_name = "مرفق أرشيفي"
        verbose_name_plural = "المرفقات الأرشيفية"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["uploaded_at"]),
        ]

    def __str__(self):
        return self.title or f"مرفق للكتاب {self.document.document_number}"

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)