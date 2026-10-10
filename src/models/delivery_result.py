"""
Project : Email Automation Toolkit
Project ID : 032

Delivery Result Model
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DeliveryResult:
    """Represent the outcome of an email delivery attempt."""

    status: str
    attempted_at: datetime
    attempt_number: int = 1
    smtp_response: str = ""
    error_message: str = ""
    delivery_id: int | None = None

    @property
    def is_success(self) -> bool:
        """Return whether the delivery attempt succeeded."""
        return self.status.upper() == "SUCCESS"

    @property
    def is_failure(self) -> bool:
        """Return whether the delivery attempt failed."""
        return self.status.upper() == "FAILED"

    @property
    def can_retry(self) -> bool:
        """Return whether the delivery attempt can be retried."""
        return self.is_failure

    @property
    def has_error(self) -> bool:
        """Return whether an error message was recorded."""
        return bool(self.error_message.strip())