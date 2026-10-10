"""
Project : Email Automation Toolkit
Project ID : 032

Delivery History Service
"""

from __future__ import annotations

from datetime import datetime

from src.models.delivery_result import DeliveryResult
from src.services.database_service import DatabaseService


class DeliveryHistoryService:
    """Persist and retrieve email delivery history."""

    def __init__(
        self,
        database_service: DatabaseService,
    ) -> None:
        self._database = database_service

    def initialize(self) -> None:
        """Create the delivery history table when required."""
        self._database.execute(
            """
            CREATE TABLE IF NOT EXISTS delivery_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_job_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,
                attempted_at TEXT NOT NULL,
                smtp_response TEXT NOT NULL DEFAULT '',
                error_message TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (email_job_id)
                    REFERENCES email_jobs(id)
            )
            """
        )

    def record_delivery(
        self,
        email_job_id: int,
        result: DeliveryResult,
    ) -> int:
        """Persist a delivery result and return its history ID."""
        if email_job_id <= 0:
            raise ValueError(
                "Email job ID must be greater than zero."
            )

        if result.attempt_number < 1:
            raise ValueError(
                "Delivery attempt number must be at least 1."
            )

        return self._database.execute(
            """
            INSERT INTO delivery_history (
                email_job_id,
                status,
                attempt_number,
                attempted_at,
                smtp_response,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                email_job_id,
                result.status,
                result.attempt_number,
                result.attempted_at.isoformat(
                    timespec="seconds"
                ),
                result.smtp_response,
                result.error_message,
            ),
        )

    def get_delivery_history(
        self,
        email_job_id: int,
    ) -> list[DeliveryResult]:
        """Return delivery attempts for an email job."""
        if email_job_id <= 0:
            raise ValueError(
                "Email job ID must be greater than zero."
            )

        rows = self._database.fetch_all(
            """
            SELECT
                id,
                status,
                attempt_number,
                attempted_at,
                smtp_response,
                error_message
            FROM delivery_history
            WHERE email_job_id = ?
            ORDER BY attempt_number, id
            """,
            (email_job_id,),
        )

        return [
            DeliveryResult(
                delivery_id=row["id"],
                status=row["status"],
                attempt_number=row["attempt_number"],
                attempted_at=datetime.fromisoformat(
                    row["attempted_at"]
                ),
                smtp_response=row["smtp_response"],
                error_message=row["error_message"],
            )
            for row in rows
        ]

    def get_latest_delivery(
        self,
        email_job_id: int,
    ) -> DeliveryResult | None:
        """Return the most recent delivery attempt."""
        history = self.get_delivery_history(
            email_job_id,
        )

        if not history:
            return None

        return history[-1]