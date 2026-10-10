"""
Project : Email Automation Toolkit
Project ID : 032

Recipient Service
"""

from __future__ import annotations

import re
from datetime import datetime

from src.models.recipient import Recipient
from src.services.database_service import DatabaseService


class RecipientService:
    """Manage email recipients and recipient groups."""

    _EMAIL_PATTERN = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    def __init__(
        self,
        database_service: DatabaseService,
    ) -> None:
        self._database = database_service

    def add_recipient(
        self,
        name: str,
        email: str,
        is_active: bool = True,
    ) -> Recipient:
        """Create a recipient or return the existing matching recipient."""
        normalized_email = email.strip().lower()
        normalized_name = name.strip()

        self._validate_email(normalized_email)

        if not normalized_name:
            raise ValueError(
                "Recipient name cannot be empty."
            )

        existing_recipient = self.get_recipient_by_email(
            normalized_email,
        )

        if existing_recipient is not None:
            return existing_recipient

        created_at = datetime.now().isoformat(
            timespec="seconds"
        )

        recipient_id = self._database.execute(
            """
            INSERT INTO recipients (
                name,
                email,
                is_active,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                normalized_name,
                normalized_email,
                int(is_active),
                created_at,
            ),
        )

        return Recipient(
            recipient_id=recipient_id,
            name=normalized_name,
            email=normalized_email,
            is_active=is_active,
        )

    def get_recipient(
        self,
        recipient_id: int,
    ) -> Recipient | None:
        """Retrieve a recipient by database ID."""
        row = self._database.fetch_one(
            """
            SELECT id, name, email, is_active
            FROM recipients
            WHERE id = ?
            """,
            (recipient_id,),
        )

        if row is None:
            return None

        return self._row_to_recipient(row)

    def get_recipient_by_email(
        self,
        email: str,
    ) -> Recipient | None:
        """Retrieve a recipient by normalized email address."""
        normalized_email = email.strip().lower()

        self._validate_email(normalized_email)

        row = self._database.fetch_one(
            """
            SELECT id, name, email, is_active
            FROM recipients
            WHERE email = ?
            """,
            (normalized_email,),
        )

        if row is None:
            return None

        return self._row_to_recipient(row)

    def list_active_recipients(self) -> list[Recipient]:
        """Return all active recipients."""
        rows = self._database.fetch_all(
            """
            SELECT id, name, email, is_active
            FROM recipients
            WHERE is_active = 1
            ORDER BY name
            """
        )

        return [
            self._row_to_recipient(row)
            for row in rows
        ]

    def set_recipient_status(
        self,
        recipient_id: int,
        is_active: bool,
    ) -> None:
        """Activate or deactivate a recipient."""
        self._database.execute(
            """
            UPDATE recipients
            SET is_active = ?
            WHERE id = ?
            """,
            (int(is_active), recipient_id),
        )

    def create_group(
        self,
        name: str,
        description: str = "",
    ) -> int:
        """Create a recipient group."""
        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError(
                "Recipient group name cannot be empty."
            )

        existing_group = self._database.fetch_one(
            """
            SELECT id
            FROM recipient_groups
            WHERE name = ?
            """,
            (normalized_name,),
        )

        if existing_group is not None:
            return int(existing_group["id"])

        created_at = datetime.now().isoformat(
            timespec="seconds"
        )

        return self._database.execute(
            """
            INSERT INTO recipient_groups (
                name,
                description,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                normalized_name,
                description.strip(),
                created_at,
            ),
        )

    def add_recipient_to_group(
        self,
        group_id: int,
        recipient_id: int,
    ) -> None:
        """Add a recipient to a group if not already present."""
        self._database.execute(
            """
            INSERT OR IGNORE INTO recipient_group_members (
                group_id,
                recipient_id
            )
            VALUES (?, ?)
            """,
            (
                group_id,
                recipient_id,
            ),
        )

    def resolve_group_recipients(
        self,
        group_id: int,
    ) -> list[Recipient]:
        """Return active recipients belonging to a group."""
        rows = self._database.fetch_all(
            """
            SELECT r.id, r.name, r.email, r.is_active
            FROM recipients AS r
            INNER JOIN recipient_group_members AS gm
                ON r.id = gm.recipient_id
            WHERE gm.group_id = ?
              AND r.is_active = 1
            ORDER BY r.name
            """,
            (group_id,),
        )

        return [
            self._row_to_recipient(
                row,
                group_id=group_id,
            )
            for row in rows
        ]

    @classmethod
    def _validate_email(
        cls,
        email: str,
    ) -> None:
        """Validate an email address."""
        if not cls._EMAIL_PATTERN.fullmatch(email):
            raise ValueError(
                f"Invalid email address: {email}"
            )

    @staticmethod
    def _row_to_recipient(
        row: object,
        group_id: int | None = None,
    ) -> Recipient:
        """Convert a database row into a Recipient model."""
        return Recipient(
            recipient_id=row["id"],
            name=row["name"],
            email=row["email"],
            is_active=bool(row["is_active"]),
            group_id=group_id,
        )