"""
Project : Email Automation Toolkit
Project ID : 032

Email Validator
"""

from __future__ import annotations

import re

from src.models.email_job import EmailJob


class EmailValidator:
    """Validate an email job before delivery."""

    _EMAIL_PATTERN = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    def validate(self, email_job: EmailJob) -> None:
        """Validate all required components of an email job."""
        self._validate_message(email_job)
        self._validate_recipients(email_job)
        self._validate_attachments(email_job)

    def _validate_message(self, email_job: EmailJob) -> None:
        """Validate the core email message."""
        message = email_job.email_message

        if not message.subject.strip():
            raise ValueError("Email subject cannot be empty.")

        if not message.sender.strip():
            raise ValueError("Email sender cannot be empty.")

        if not message.has_html_body and not message.has_text_body:
            raise ValueError(
                "Email must contain an HTML body, "
                "a plain-text body, or both."
            )

    def _validate_recipients(self, email_job: EmailJob) -> None:
        """Validate all recipients associated with the email job."""
        recipients = email_job.email_message.all_recipients

        if not recipients:
            raise ValueError(
                "At least one email recipient is required."
            )

        for recipient in recipients:
            normalized_recipient = recipient.strip()

            if not self._EMAIL_PATTERN.fullmatch(
                normalized_recipient
            ):
                raise ValueError(
                    f"Invalid email recipient: {recipient}"
                )

    def _validate_attachments(self, email_job: EmailJob) -> None:
        """Validate every attachment associated with the email job."""
        for attachment in email_job.attachments:
            if not attachment.file_path.is_file():
                raise FileNotFoundError(
                    f"Attachment file not found: "
                    f"{attachment.file_path}"
                )

            if attachment.file_size < 0:
                raise ValueError(
                    f"Invalid attachment size: "
                    f"{attachment.file_path}"
                )

            if not attachment.mime_type.strip():
                raise ValueError(
                    f"Attachment MIME type is empty: "
                    f"{attachment.file_path}"
                )