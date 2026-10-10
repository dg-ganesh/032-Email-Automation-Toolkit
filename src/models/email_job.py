"""
Project : Email Automation Toolkit
Project ID : 032

Email Job Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.models.attachment import Attachment
from src.models.email_message import EmailMessage


@dataclass
class EmailJob:
    """Represent a complete email job prepared for delivery."""

    email_message: EmailMessage
    attachments: list[Attachment] = field(default_factory=list)
    template_name: str = ""
    job_id: int | None = None
    status: str = "READY"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def attachment_count(self) -> int:
        """Return the number of attachments associated with the job."""
        return len(self.attachments)

    @property
    def recipient_count(self) -> int:
        """Return the total number of recipients in the email job."""
        return len(self.email_message.all_recipients)

    @property
    def is_ready(self) -> bool:
        """Return whether the job is marked as ready for delivery."""
        return self.status.upper() == "READY"