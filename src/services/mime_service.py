"""
Project : Email Automation Toolkit
Project ID : 032

MIME Message Service
"""

from __future__ import annotations

from email.message import EmailMessage
from pathlib import Path

from src.models.email_job import EmailJob


class MIMEMessageService:
    """Build MIME email messages from EmailJob objects."""

    def build_message(
        self,
        email_job: EmailJob,
    ) -> EmailMessage:
        """Build a MIME message from an email job."""
        message = EmailMessage()

        email_message = email_job.email_message

        message["Subject"] = email_message.subject
        message["From"] = email_message.sender

        if email_message.recipients:
            message["To"] = ", ".join(
                email_message.recipients
            )

        if email_message.cc_recipients:
            message["Cc"] = ", ".join(
                email_message.cc_recipients
            )

        if email_message.bcc_recipients:
            message["Bcc"] = ", ".join(
                email_message.bcc_recipients
            )

        if email_message.text_body.strip():
            message.set_content(
                email_message.text_body,
            )
        else:
            message.set_content("")

        if email_message.html_body.strip():
            message.add_alternative(
                email_message.html_body,
                subtype="html",
            )

        for attachment in email_job.attachments:
            self._add_attachment(
                message=message,
                file_path=attachment.file_path,
                mime_type=attachment.mime_type,
            )

        return message

    @staticmethod
    def _add_attachment(
        message: EmailMessage,
        file_path: Path,
        mime_type: str,
    ) -> None:
        """Add a validated file attachment to a MIME message."""
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Attachment file not found: {file_path}"
            )

        mime_parts = mime_type.split(
            "/",
            maxsplit=1,
        )

        if len(mime_parts) != 2:
            raise ValueError(
                f"Invalid MIME type: {mime_type}"
            )

        maintype, subtype = mime_parts

        file_data = file_path.read_bytes()

        message.add_attachment(
            file_data,
            maintype=maintype,
            subtype=subtype,
            filename=file_path.name,
        )