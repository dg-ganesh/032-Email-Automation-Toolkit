
"""
Project : Email Automation Toolkit
Project ID : 032

Recipient CSV Import Service
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from src.services.recipient_file_service import RecipientFileService
from src.services.recipient_service import RecipientService


class RecipientImportService:
    """Import CSV recipients into the application's recipient database."""

    def __init__(
        self,
        recipient_file_service: RecipientFileService,
        recipient_service: RecipientService,
    ) -> None:
        self._recipient_file_service = recipient_file_service
        self._recipient_service = recipient_service

    def import_recipients(self) -> dict[str, Any]:
        """Import active CSV recipients and assign their groups."""
        summary: dict[str, Any] = {
            "csv_rows": 0,
            "recipients_created": 0,
            "recipients_existing": 0,
            "recipients_activated": 0,
            "group_assignments_processed": 0,
            "errors": [],
        }

        try:
            rows = self._recipient_file_service.load_recipients()
        except (OSError, ValueError, csv.Error) as exc:
            summary["errors"].append(f"CSV import aborted: {exc}")
            return summary

        summary["csv_rows"] = len(rows)
        group_ids: dict[str, int] = {}

        for row_number, row in enumerate(rows, start=2):
            try:
                name = str(row["name"]).strip()
                email = str(row["email"]).strip().lower()
                group_name = str(row["group"]).strip()

                existing = (
                    self._recipient_service.get_recipient_by_email(email)
                )

                if existing is None:
                    recipient = self._recipient_service.add_recipient(
                        name=name,
                        email=email,
                        is_active=True,
                    )
                    summary["recipients_created"] += 1
                else:
                    recipient = existing
                    summary["recipients_existing"] += 1

                    if not recipient.is_active:
                        if recipient.recipient_id is None:
                            raise ValueError(
                                "Existing recipient has no database ID."
                            )

                        self._recipient_service.set_recipient_status(
                            recipient.recipient_id,
                            True,
                        )
                        summary["recipients_activated"] += 1

                if recipient.recipient_id is None:
                    raise ValueError(
                        "Recipient has no database ID after retrieval."
                    )

                group_key = group_name.casefold()

                if group_key not in group_ids:
                    group_ids[group_key] = (
                        self._recipient_service.create_group(group_name)
                    )

                self._recipient_service.add_recipient_to_group(
                    group_id=group_ids[group_key],
                    recipient_id=recipient.recipient_id,
                )

                summary["group_assignments_processed"] += 1

            except (KeyError, TypeError, ValueError, OSError) as exc:
                summary["errors"].append(
                    f"CSV row {row_number}: {exc}"
                )
            except Exception as exc:
                summary["errors"].append(
                    f"CSV row {row_number}: Unexpected error: {exc}"
                )

        return summary

    @staticmethod
    def validate_csv_path(csv_path: Path) -> Path:
        """Validate and return an existing CSV file path."""
        path = Path(csv_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Recipient CSV file not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Recipient CSV path is not a file: {path}"
            )

        if path.suffix.lower() != ".csv":
            raise ValueError(
                f"Recipient file must have a .csv extension: {path}"
            )

        return path

