from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from django.db import models

if TYPE_CHECKING:
    pass


class QuerySet[T: models.Model](models.QuerySet[T]):
    """Custom QuerySet with additional helper methods."""

    def get_or_none(self, *args: Any, **kwargs: Any) -> T | None:
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    async def aget_or_none(self, *args: Any, **kwargs: Any) -> T | None:
        try:
            return await super().aget(*args, **kwargs)
        except self.model.DoesNotExist:
            return None


if TYPE_CHECKING:

    class Manager[T: models.Model](models.Manager[T], QuerySet[T]):
        pass

else:

    class Manager[T: models.Model](models.Manager[T].from_queryset(QuerySet)):
        pass


class ReportConfig(models.Model):
    report_channel_id = models.BigIntegerField(
        unique=True, help_text="Discord channel ID where reports will be sent"
    )
    enabled = models.BooleanField(
        default=True, help_text="Whether the report system is enabled"
    )

    objects: Manager[Self] = Manager()

    class Meta:
        managed = True
        db_table = "report_config"
        verbose_name = "Report Configuration"
        verbose_name_plural = "Report Configurations"

    def __str__(self) -> str:
        return f"Report Config for Channel {self.report_channel_id}"


class Report(models.Model):
    """Model representing a user report."""

    REPORT_TYPE_CHOICES = [
        ("violation", "Report Violation"),
        ("bug", "Report Bug"),
        ("suggestion", "Provide Suggestion"),
        ("other", "Other"),
    ]

    user_id = models.BigIntegerField(help_text="Discord user ID of the reporter")
    user_name = models.CharField(
        max_length=255, help_text="Discord username of the reporter"
    )
    report_type = models.CharField(
        max_length=20, choices=REPORT_TYPE_CHOICES, help_text="Type of report"
    )
    content = models.TextField(help_text="Report content")

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the report was created"
    )

    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="Metadata about attachments (filename, url, etc.)",
    )

    replied = models.BooleanField(default=False, help_text="Whether admin replied")
    reply_time = models.DateTimeField(
        null=True, blank=True, help_text="When the reply was sent"
    )
    reply_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Username of the admin who replied",
    )
    reply_content = models.TextField(
        null=True, blank=True, help_text="Content of the admin's reply"
    )

    discord_message_id = models.BigIntegerField(
        null=True, blank=True, help_text="ID of the report message in Discord"
    )

    objects: Manager[Self] = Manager()

    class Meta:
        managed = True
        db_table = "report"
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["report_type"]),
            models.Index(fields=["replied"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Report #{self.pk} - {self.get_report_type_display()} by {self.user_name}"

    @property
    def status(self) -> str:
        """Return the current status of the report."""
        return "Replied" if self.replied else "Pending"
