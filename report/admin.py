from django.contrib import admin
from django.utils.html import format_html

from .models import Report, ReportConfig


@admin.register(ReportConfig)
class ReportConfigAdmin(admin.ModelAdmin):
    list_display = ("report_channel_id", "enabled")
    list_filter = ("enabled",)
    search_fields = ("report_channel_id",)
    fieldsets = (
        (
            "Discord Configuration",
            {
                "fields": ("report_channel_id",),
            },
        ),
        (
            "Settings",
            {
                "fields": ("enabled",),
            },
        ),
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "report_type",
        "user_name",
        "status_badge",
        "created_at",
        "replied",
    )
    list_filter = ("report_type", "replied", "created_at")
    search_fields = ("user_name", "user_id", "content", "reply_content")
    readonly_fields = (
        "id",
        "user_id",
        "user_name",
        "created_at",
        "discord_message_id",
    )
    fieldsets = (
        (
            "Report Information",
            {
                "fields": (
                    "id",
                    "user_id",
                    "user_name",
                    "report_type",
                    "content",
                    "created_at",
                ),
            },
        ),
        (
            "Attachments",
            {
                "fields": ("attachments",),
                "classes": ("collapse",),
            },
        ),
        (
            "Reply Information",
            {
                "fields": (
                    "replied",
                    "reply_time",
                    "reply_by",
                    "reply_content",
                ),
            },
        ),
        (
            "Discord Tracking",
            {
                "fields": ("discord_message_id",),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"



    def has_add_permission(self, request):
        """Disable manual report creation - reports should come from Discord."""
        return False
