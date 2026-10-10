"""
Project : Email Automation Toolkit
Project ID : 032

Schedule Service
"""

from __future__ import annotations

from datetime import datetime

from src.models.schedule import Schedule
from src.services.database_service import DatabaseService


class ScheduleService:
    """
    Persists and manages email workflow schedules.
    """

    def __init__(
        self,
        database_service: DatabaseService,
    ) -> None:
        self._database = database_service

    def initialize(self) -> None:
        """Create the schedules table when it does not exist."""
        self._database.execute(
            """
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_type TEXT NOT NULL,
                scheduled_at TEXT NOT NULL,
                interval_minutes INTEGER,
                is_active INTEGER NOT NULL DEFAULT 1
            )
            """
        )

    def create_schedule(
        self,
        schedule: Schedule,
    ) -> int:
        """Persist a schedule and return its generated ID."""
        if schedule.schedule_id is not None:
            raise ValueError(
                "A new schedule cannot already have a schedule ID."
            )

        schedule_id = self._database.execute(
            """
            INSERT INTO schedules (
                schedule_type,
                scheduled_at,
                interval_minutes,
                is_active
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                schedule.schedule_type,
                schedule.scheduled_at.isoformat(
                    timespec="seconds"
                ),
                schedule.interval_minutes,
                int(schedule.is_active),
            ),
        )

        if not schedule_id:
            raise RuntimeError(
                "Schedule creation did not return an ID."
            )

        return schedule_id

    def get_schedule(
        self,
        schedule_id: int,
    ) -> Schedule | None:
        """Retrieve a schedule by ID."""
        if schedule_id <= 0:
            raise ValueError(
                "Schedule ID must be greater than zero."
            )

        row = self._database.fetch_one(
            """
            SELECT
                id,
                schedule_type,
                scheduled_at,
                interval_minutes,
                is_active
            FROM schedules
            WHERE id = ?
            """,
            (schedule_id,),
        )

        if row is None:
            return None

        return self._row_to_schedule(row)

    def get_all_schedules(self) -> list[Schedule]:
        """Return all schedules ordered by scheduled time."""
        rows = self._database.fetch_all(
            """
            SELECT
                id,
                schedule_type,
                scheduled_at,
                interval_minutes,
                is_active
            FROM schedules
            ORDER BY scheduled_at, id
            """
        )

        return [
            self._row_to_schedule(row)
            for row in rows
        ]

    def get_active_schedules(self) -> list[Schedule]:
        """Return all currently active schedules."""
        rows = self._database.fetch_all(
            """
            SELECT
                id,
                schedule_type,
                scheduled_at,
                interval_minutes,
                is_active
            FROM schedules
            WHERE is_active = 1
            ORDER BY scheduled_at, id
            """
        )

        return [
            self._row_to_schedule(row)
            for row in rows
        ]

    def activate_schedule(
        self,
        schedule_id: int,
    ) -> Schedule:
        """Activate an existing schedule."""
        schedule = self._require_schedule(
            schedule_id,
        )

        if schedule.is_active:
            return schedule

        self._database.execute(
            """
            UPDATE schedules
            SET is_active = 1
            WHERE id = ?
            """,
            (schedule_id,),
        )

        updated_schedule = self.get_schedule(
            schedule_id,
        )

        if updated_schedule is None:
            raise RuntimeError(
                "Schedule could not be retrieved after activation."
            )

        return updated_schedule

    def deactivate_schedule(
        self,
        schedule_id: int,
    ) -> Schedule:
        """Deactivate an existing schedule."""
        schedule = self._require_schedule(
            schedule_id,
        )

        if not schedule.is_active:
            return schedule

        self._database.execute(
            """
            UPDATE schedules
            SET is_active = 0
            WHERE id = ?
            """,
            (schedule_id,),
        )

        updated_schedule = self.get_schedule(
            schedule_id,
        )

        if updated_schedule is None:
            raise RuntimeError(
                "Schedule could not be retrieved after deactivation."
            )

        return updated_schedule

    def delete_schedule(
        self,
        schedule_id: int,
    ) -> None:
        """Delete an existing schedule."""
        self._require_schedule(
            schedule_id,
        )

        self._database.execute(
            """
            DELETE FROM schedules
            WHERE id = ?
            """,
            (schedule_id,),
        )

    def _require_schedule(
        self,
        schedule_id: int,
    ) -> Schedule:
        """Return a schedule or raise when it does not exist."""
        schedule = self.get_schedule(
            schedule_id,
        )

        if schedule is None:
            raise ValueError(
                f"Schedule {schedule_id} does not exist."
            )

        return schedule

    @staticmethod
    def _row_to_schedule(row) -> Schedule:
        """Convert a database row into a Schedule model."""
        scheduled_at = datetime.fromisoformat(
            row["scheduled_at"],
        )

        interval_minutes = row["interval_minutes"]

        return Schedule(
            schedule_id=row["id"],
            schedule_type=row["schedule_type"],
            scheduled_at=scheduled_at,
            interval_minutes=interval_minutes,
            is_active=bool(row["is_active"]),
        )