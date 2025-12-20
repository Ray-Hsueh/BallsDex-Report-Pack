import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING, Optional
from django.utils import timezone

from ..models import Report, ReportConfig

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


REPORT_TYPES = [
    ("Report Violation", "violation"),
    ("Report Bug", "bug"),
    ("Provide Suggestion", "suggestion"),
    ("Other", "other"),
]


class ReportCog(commands.Cog, name="Report"):
    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self.report_messages = {}

    @app_commands.command(
        name="report", description="Report issues or suggestions to the backend server"
    )
    @app_commands.describe(
        report_type="Select report type",
        content="Please describe your issue or suggestion in detail",
        attachment="Optional: Attach files",
    )
    @app_commands.choices(
        report_type=[
            app_commands.Choice(name=label, value=value) for label, value in REPORT_TYPES
        ]
    )
    async def report(
        self,
        interaction: discord.Interaction,
        report_type: app_commands.Choice[str],
        content: str,
        attachment: Optional[discord.Attachment] = None,
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        config = await ReportConfig.objects.aget_or_none(enabled=True)
        if not config:
            await interaction.followup.send(
                "❌ Report system is not configured. Please contact an administrator.",
                ephemeral=True,
            )
            return

        attachments_meta = []
        if attachment is not None:
            attachments_meta.append(
                {
                    "id": getattr(attachment, "id", None),
                    "filename": attachment.filename,
                    "content_type": getattr(attachment, "content_type", None),
                    "size": getattr(attachment, "size", None),
                    "url": attachment.url,
                }
            )

        report = await Report.objects.acreate(
            user_id=interaction.user.id,
            user_name=str(interaction.user),
            report_type=report_type.value,
            content=content,
            attachments=attachments_meta,
        )

        embed = discord.Embed(
            title=f"New User Report Received (ID: {report.pk})",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Report Type", value=report_type.name, inline=False)
        embed.add_field(name="Content", value=content, inline=False)
        embed.add_field(name="Report ID", value=str(report.pk), inline=False)
        embed.add_field(name="Status", value="Pending", inline=False)
        if attachment is not None:
            embed.add_field(name="files", value=attachment.filename, inline=False)
            if getattr(attachment, "content_type", "").startswith("image/"):
                embed.set_image(url=f"attachment://{attachment.filename}")
        embed.set_footer(text=f"From {interaction.user} ({interaction.user.id})")
        embed.timestamp = discord.utils.utcnow()

        view = ReportReplyView(self, report.pk, report)

        channel = self.bot.get_channel(config.report_channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            files = []
            if attachment is not None:
                try:
                    files = [await attachment.to_file()]
                except Exception:
                    files = []
            message = await channel.send(embed=embed, view=view, files=files)
            self.report_messages[report.pk] = message

            report.discord_message_id = message.id
            await report.asave(update_fields=["discord_message_id"])

            if attachment is not None and message.attachments:
                uploaded_attachments = [
                    {
                        "filename": a.filename,
                        "url": a.url,
                        "content_type": getattr(a, "content_type", None),
                        "size": getattr(a, "size", None),
                    }
                    for a in message.attachments
                ]
                report.attachments = uploaded_attachments
                await report.asave(update_fields=["attachments"])

            await interaction.followup.send(
                f"✅ Report submitted successfully! Your report ID is {report.pk}. You will be notified of any updates via DM.",
                ephemeral=True,
            )
            try:
                await interaction.user.send(
                    f"Hello, we have received your report (ID: {report.pk}, Type: {report_type.name}). Our administrators will process it.\nYou will be notified of any updates via DM. Thank you for your assistance!"
                )
            except Exception:
                pass
            return

        await interaction.followup.send(
            "❌ Report submission failed. Please contact an administrator.",
            ephemeral=True,
        )


class ReportReplyView(discord.ui.View):
    def __init__(self, cog: ReportCog, report_id: int, report: Report):
        super().__init__(timeout=None)
        self.cog = cog
        self.report_id = report_id
        self.report = report

    @discord.ui.button(label="Reply", style=discord.ButtonStyle.primary)
    async def reply_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Only administrators can use this feature.", ephemeral=True
            )
            return

        modal = ReportReplyModal(self.cog, self.report_id, self.report)
        await interaction.response.send_modal(modal)


class ReportReplyModal(discord.ui.Modal, title="Reply to Report"):
    def __init__(self, cog: ReportCog, report_id: int, report: Report):
        super().__init__()
        self.cog = cog
        self.report_id = report_id
        self.report = report
        self.reply_content = discord.ui.TextInput(
            label="Reply Content",
            placeholder="Enter your reply...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000,
        )
        self.add_item(self.reply_content)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        report = await Report.objects.aget_or_none(pk=self.report_id)
        if not report:
            await interaction.followup.send(
                f"❌ Report ID {self.report_id} not found.", ephemeral=True
            )
            return

        report.replied = True
        report.reply_time = timezone.now()
        report.reply_by = str(interaction.user)
        report.reply_content = self.reply_content.value
        await report.asave(
            update_fields=["replied", "reply_time", "reply_by", "reply_content"]
        )

        if self.report_id in self.cog.report_messages:
            original_message = self.cog.report_messages[self.report_id]
            original_embed = original_message.embeds[0]
            original_embed.color = discord.Color.green()
            for i, field in enumerate(original_embed.fields):
                if field.name == "Status":
                    original_embed.set_field_at(
                        i, name="Status", value="Replied", inline=False
                    )
                    break
            view = ReportReplyView(self.cog, self.report_id, report)
            for item in view.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
            await original_message.edit(embed=original_embed, view=view)

        embed = discord.Embed(
            title=f"Administrator Reply (Report ID: {self.report_id})",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Report Type", value=report.get_report_type_display(), inline=False
        )
        embed.add_field(name="Original Content", value=report.content, inline=False)

        if report.attachments:
            attachment_lines = []
            for a in report.attachments:
                url = a.get("url")
                name = a.get("filename") or "files"
                if url:
                    attachment_lines.append(f"[{name}]({url})")
            if attachment_lines:
                embed.add_field(
                    name="report files", value="\n".join(attachment_lines), inline=False
                )

        embed.add_field(
            name="Administrator Reply", value=self.reply_content.value, inline=False
        )
        embed.set_footer(text=f"Replied by: {interaction.user} ({interaction.user.id})")
        embed.timestamp = discord.utils.utcnow()

        config = await ReportConfig.objects.aget_or_none(enabled=True)
        if config:
            channel = self.cog.bot.get_channel(config.report_channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                await channel.send(embed=embed)
                await interaction.followup.send(
                    f"✅ Reply sent successfully.", ephemeral=True
                )

                try:
                    user = await self.cog.bot.fetch_user(report.user_id)
                    await user.send(
                        f"Hello, your report (ID: {self.report_id}, Type: {report.get_report_type_display()}) has received an administrator reply:\n"
                        f"{self.reply_content.value}"
                    )
                except Exception as e:
                    print(f"Error sending DM: {str(e)}")
                return

        await interaction.followup.send(
            "❌ Reply failed. Please contact an administrator.", ephemeral=True
        )


async def setup(bot: "BallsDexBot"):
    await bot.add_cog(ReportCog(bot))
