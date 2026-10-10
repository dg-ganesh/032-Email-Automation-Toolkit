
"""
Project : Email Automation Toolkit
Project ID : 032

Recipient Import Service Integration Tests
"""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.services.database_service import DatabaseService
from src.services.recipient_file_service import RecipientFileService
from src.services.recipient_import_service import RecipientImportService
from src.services.recipient_service import RecipientService


class TestRecipientImportService(unittest.TestCase):
    """Test CSV recipient imports using an isolated SQLite database."""

    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_directory.name)

        self.database = DatabaseService(self.test_root / "test.db")
        self.database.initialize()

        self.recipient_service = RecipientService(self.database)
        self.csv_path = self.test_root / "recipients.csv"

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def write_csv(
        self,
        rows: list[dict[str, str]],
        fieldnames: list[str] | None = None,
    ) -> None:
        """Write test recipient data to a temporary CSV."""
        columns = fieldnames or ["name", "email", "group", "active"]

        with self.csv_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def create_importer(self) -> RecipientImportService:
        """Create the CSV importer for the test database."""
        return RecipientImportService(
            recipient_file_service=RecipientFileService(self.csv_path),
            recipient_service=self.recipient_service,
        )

    def count_rows(self, table: str) -> int:
        """Count records in a known application table."""
        allowed_tables = {
            "recipients",
            "recipient_groups",
            "recipient_group_members",
        }
        if table not in allowed_tables:
            raise ValueError(f"Unsupported test table: {table}")

        row = self.database.fetch_one(
            f"SELECT COUNT(*) AS total FROM {table}"
        )
        assert row is not None
        return int(row["total"])

    def test_import_creates_recipients_and_groups(self) -> None:
        self.write_csv([
            {
                "name": "Person One",
                "email": "one@example.com",
                "group": "Finance",
                "active": "true",
            },
            {
                "name": "Person Two",
                "email": "two@example.com",
                "group": "Management",
                "active": "true",
            },
        ])

        result = self.create_importer().import_recipients()

        self.assertEqual(result["recipients_created"], 2)
        self.assertEqual(result["group_assignments_processed"], 2)
        self.assertEqual(result["errors"], [])
        self.assertEqual(self.count_rows("recipients"), 2)
        self.assertEqual(self.count_rows("recipient_groups"), 2)
        self.assertEqual(self.count_rows("recipient_group_members"), 2)

    def test_repeated_import_does_not_create_duplicates(self) -> None:
        self.write_csv([
            {
                "name": "Person One",
                "email": "one@example.com",
                "group": "Finance",
                "active": "true",
            },
        ])

        importer = self.create_importer()
        importer.import_recipients()
        second_result = importer.import_recipients()

        self.assertEqual(second_result["recipients_created"], 0)
        self.assertEqual(second_result["recipients_existing"], 1)
        self.assertEqual(self.count_rows("recipients"), 1)
        self.assertEqual(self.count_rows("recipient_groups"), 1)
        self.assertEqual(self.count_rows("recipient_group_members"), 1)

    def test_existing_recipient_is_reused(self) -> None:
        self.recipient_service.add_recipient(
            name="Existing Person",
            email="existing@example.com",
        )

        self.write_csv([
            {
                "name": "Existing Person",
                "email": "existing@example.com",
                "group": "Finance",
                "active": "true",
            },
        ])

        result = self.create_importer().import_recipients()

        self.assertEqual(result["recipients_created"], 0)
        self.assertEqual(result["recipients_existing"], 1)
        self.assertEqual(self.count_rows("recipients"), 1)

    def test_inactive_existing_recipient_is_reactivated(self) -> None:
        recipient = self.recipient_service.add_recipient(
            name="Inactive Person",
            email="inactive@example.com",
        )
        self.recipient_service.set_recipient_status(
            recipient.recipient_id,
            False,
        )

        self.write_csv([
            {
                "name": "Inactive Person",
                "email": "inactive@example.com",
                "group": "Finance",
                "active": "true",
            },
        ])

        result = self.create_importer().import_recipients()
        updated = self.recipient_service.get_recipient_by_email(
            "inactive@example.com"
        )

        self.assertEqual(result["recipients_activated"], 1)
        self.assertIsNotNone(updated)
        self.assertTrue(updated.is_active)

    def test_invalid_csv_is_reported(self) -> None:
        self.write_csv(
            [
                {
                    "name": "",
                    "email": "bad@example.com",
                    "group": "Finance",
                    "active": "true",
                },
            ]
        )

        result = self.create_importer().import_recipients()

        self.assertEqual(result["recipients_created"], 0)
        self.assertTrue(result["errors"])
        self.assertEqual(self.count_rows("recipients"), 0)

    def test_missing_csv_is_reported(self) -> None:
        result = self.create_importer().import_recipients()

        self.assertEqual(result["recipients_created"], 0)
        self.assertTrue(result["errors"])
        self.assertIn("CSV import aborted", result["errors"][0])

    def test_inactive_csv_rows_are_skipped(self) -> None:
        self.write_csv([
            {
                "name": "Inactive CSV Person",
                "email": "inactive@example.com",
                "group": "Finance",
                "active": "false",
            },
        ])

        result = self.create_importer().import_recipients()

        self.assertEqual(result["csv_rows"], 0)
        self.assertEqual(result["recipients_created"], 0)
        self.assertEqual(self.count_rows("recipients"), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
