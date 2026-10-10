"""
Project : Email Automation Toolkit
Project ID : 032

Recipient Model
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Recipient:
    """Represent an email recipient."""

    name: str
    email: str
    is_active: bool = True
    group_id: int | None = None
    recipient_id: int | None = None

    @property
    def display_name(self) -> str:
        """Return the recipient name when available, otherwise the email."""
        return self.name.strip() or self.email.strip()

    @property
    def normalized_email(self) -> str:
        """Return the normalized email address."""
        return self.email.strip().lower()