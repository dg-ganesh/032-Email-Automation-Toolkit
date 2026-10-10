"""
Project : Email Automation Toolkit
Project ID : 032

Email Builder
"""

from __future__ import annotations

from src.models.attachment import Attachment
from src.models.email_job import EmailJob
from src.models.email_message import EmailMessage
from src.models.recipient import Recipient


class EmailBuilder:
    """Build complete email jobs from validated components."""

    DELIVERY_MODE_SHARED = "SHARED"
    DELIVERY_MODE_INDIVIDUAL = "INDIVIDUAL"

    @classmethod
    def normalize_delivery_mode(cls, mode: str) -> str:
        """Validate and normalize the selected multiple-recipient mode."""
        normalized = mode.strip().upper()

        if normalized not in {
            cls.DELIVERY_MODE_SHARED,
            cls.DELIVERY_MODE_INDIVIDUAL,
        }:
            raise ValueError(
                "Delivery mode must be SHARED or INDIVIDUAL."
            )

        return normalized

    def build(
        self,
        subject: str,
        sender: str,
        recipients: list[str],
        html_body: str,
        text_body: str,
        cc_recipients: list[str] | None = None,
        bcc_recipients: list[str] | None = None,
        attachments: list[Attachment] | None = None,
        template_name: str = "",
    ) -> EmailJob:
        """Build an email job from email content and attachments."""
        message = EmailMessage(
            subject=subject.strip(),
            sender=sender.strip(),
            recipients=self._clean_recipients(recipients),
            cc_recipients=self._clean_recipients(
                cc_recipients or []
            ),
            bcc_recipients=self._clean_recipients(
                bcc_recipients or []
            ),
            html_body=html_body,
            text_body=text_body,
        )

        return EmailJob(
            email_message=message,
            attachments=list(attachments or []),
            template_name=template_name.strip(),
        )

    def build_from_recipients(
        self,
        subject: str,
        sender: str,
        recipients: list[Recipient],
        html_body: str,
        text_body: str,
        cc_recipients: list[Recipient] | None = None,
        bcc_recipients: list[Recipient] | None = None,
        attachments: list[Attachment] | None = None,
        template_name: str = "",
    ) -> EmailJob:
        """Build an email job from managed recipient models."""
        return self.build(
            subject=subject,
            sender=sender,
            recipients=[
                recipient.normalized_email
                for recipient in recipients
                if recipient.is_active
            ],
            html_body=html_body,
            text_body=text_body,
            cc_recipients=[
                recipient.normalized_email
                for recipient in (cc_recipients or [])
                if recipient.is_active
            ],
            bcc_recipients=[
                recipient.normalized_email
                for recipient in (bcc_recipients or [])
                if recipient.is_active
            ],
            attachments=attachments,
            template_name=template_name,
        )

    @staticmethod
    def _clean_recipients(
        recipients: list[str],
    ) -> list[str]:
        """Normalize recipient strings and remove empty entries."""
        return [
            recipient.strip().lower()
            for recipient in recipients
            if recipient.strip()
        ]