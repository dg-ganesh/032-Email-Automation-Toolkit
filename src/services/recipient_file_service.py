"""
Project : Email Automation Toolkit
Project ID : 032

Recipient CSV File Service
"""

from __future__ import annotations

import csv
from pathlib import Path

from src.models.recipient import Recipient


class RecipientFileService:
    """Load and validate recipient records from a CSV file."""

    REQUIRED_COLUMNS = ("name", "email", "group", "active")

    def __init__(self, csv_path: Path) -> None:
        """Initialize the service with the recipient CSV path."""
        self._csv_path = Path(csv_path)

    def load_recipients(self) -> list[dict[str, str | bool]]:
        """
        Load active recipient rows from CSV.

        Returns dictionaries with name, email, group, and active fields.
        Raises ValueError with a row number when a row is invalid.
        """
        if not self._csv_path.is_file():
            raise FileNotFoundError(
                f"Recipient CSV file not found: {self._csv_path}"
            )

        recipients: list[dict[str, str | bool]] = []
        seen_emails: set[str] = set()

        with self._csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise ValueError("Recipient CSV is empty or has no header.")

            normalized_headers = [
                header.strip().lower()
                for header in reader.fieldnames
                if header is not None
            ]

            missing_columns = [
                column
                for column in self.REQUIRED_COLUMNS
                if column not in normalized_headers
            ]

            if missing_columns:
                raise ValueError(
                    "Recipient CSV is missing required columns: "
                    + ", ".join(missing_columns)
                )

            for row_number, raw_row in enumerate(reader, start=2):
                row = {
                    (key.strip().lower() if key else ""): (
                        value.strip() if value is not None else ""
                    )
                    for key, value in raw_row.items()
                    if key is not None
                }

                name = row.get("name", "")
                email = row.get("email", "").strip().lower()
                group = row.get("group", "")
                active_text = row.get("active", "").strip().lower()

                if not any((name, email, group, active_text)):
                    continue

                if not name:
                    raise ValueError(
                        f"Row {row_number}: name must not be empty."
                    )

                if not email or "@" not in email:
                    raise ValueError(
                        f"Row {row_number}: invalid email address: {email!r}"
                    )

                if not group:
                    raise ValueError(
                        f"Row {row_number}: group must not be empty."
                    )

                if active_text not in {"true", "false", "yes", "no", "1", "0"}:
                    raise ValueError(
                        f"Row {row_number}: active must be true/false, yes/no, or 1/0."
                    )

                active = active_text in {"true", "yes", "1"}

                if not active:
                    continue

                if email in seen_emails:
                    raise ValueError(
                        f"Row {row_number}: duplicate active email address: {email}"
                    )

                seen_emails.add(email)
                recipients.append(
                    {
                        "name": name,
                        "email": email,
                        "group": group,
                        "active": active,
                    }
                )

        return recipients

    def load_recipient_models(self) -> list[Recipient]:
        """
        Convert active CSV rows into the existing Recipient model.

        CSV rows are returned as Recipient instances with no database ID.
        """
        rows = self.load_recipients()
        models: list[Recipient] = []

        for row in rows:
            models.append(
                Recipient(
                    recipient_id=None,
                    name=str(row["name"]),
                    email=str(row["email"]),
                    group_name=str(row["group"]),
                    is_active=bool(row["active"]),
                )
            )

        return models

    def list_groups(self) -> list[str]:
        """Return unique groups from active recipients in sorted order."""
        groups = {
            str(row["group"])
            for row in self.load_recipients()
        }
        return sorted(groups)
