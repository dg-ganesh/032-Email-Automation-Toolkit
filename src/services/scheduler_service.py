"""
Project : Email Automation Toolkit
Project ID : 032

Scheduler Service
"""

from __future__ import annotations

from datetime import datetime, timedelta

from src.models.schedule import Schedule
from src.services.schedule_service import ScheduleService


class SchedulerService:
    """
    Determines due schedules and calculates recurring
    execution times.
    """

    def __init__(
        self,
        schedule_service: ScheduleService,
    ) -> None:
        self._schedule_service = schedule_service

    def get_due_schedules(
        self,
        current_time: datetime | None = None,
    ) -> list[Schedule]:
        """
        Return active schedules whose scheduled time
        has been reached.
        """
        if current_time is None:
            current_time = datetime.now()

        if not isinstance(current_time, datetime):
            raise TypeError(
                "Current time must be a datetime value."
            )

        active_schedules = (
            self._schedule_service.get_active_schedules()
        )

        return [
            schedule
            for schedule in active_schedules
            if schedule.scheduled_at <= current_time
        ]

    def is_due(
        self,
        schedule: Schedule,
        current_time: datetime | None = None,
    ) -> bool:
        """Determine whether an individual schedule is due."""
        if current_time is None:
            current_time = datetime.now()

        if not isinstance(current_time, datetime):
            raise TypeError(
                "Current time must be a datetime value."
            )

        if not schedule.is_active:
            return False

        return schedule.scheduled_at <= current_time

    def calculate_next_run(
        self,
        schedule: Schedule,
        current_time: datetime | None = None,
    ) -> datetime | None:
        """
        Calculate the next execution time.

        One-time schedules return None after becoming due.

        Recurring schedules advance from the scheduled time
        until the next occurrence is in the future.
        """
        if current_time is None:
            current_time = datetime.now()

        if not isinstance(current_time, datetime):
            raise TypeError(
                "Current time must be a datetime value."
            )

        if not schedule.is_active:
            return None

        if schedule.is_one_time:
            if schedule.scheduled_at <= current_time:
                return None

            return schedule.scheduled_at

        if schedule.interval_minutes is None:
            raise ValueError(
                "Recurring schedule must have an interval."
            )

        interval = timedelta(
            minutes=schedule.interval_minutes,
        )

        next_run = schedule.scheduled_at

        while next_run <= current_time:
            next_run += interval

        return next_run

    def advance_schedule(
        self,
        schedule: Schedule,
        execution_time: datetime | None = None,
    ) -> Schedule:
        """
        Return a schedule positioned at its next recurring
        execution time.

        One-time schedules become inactive after execution.
        """
        if execution_time is None:
            execution_time = datetime.now()

        if not isinstance(execution_time, datetime):
            raise TypeError(
                "Execution time must be a datetime value."
            )

        if schedule.is_one_time:
            return Schedule(
                schedule_id=schedule.schedule_id,
                schedule_type=schedule.schedule_type,
                scheduled_at=schedule.scheduled_at,
                interval_minutes=None,
                is_active=False,
            )

        next_run = self.calculate_next_run(
            schedule=schedule,
            current_time=execution_time,
        )

        if next_run is None:
            raise RuntimeError(
                "Recurring schedule could not calculate "
                "its next execution time."
            )

        return Schedule(
            schedule_id=schedule.schedule_id,
            schedule_type=schedule.schedule_type,
            scheduled_at=next_run,
            interval_minutes=schedule.interval_minutes,
            is_active=schedule.is_active,
        )

    def get_next_run(
        self,
        schedule_id: int,
        current_time: datetime | None = None,
    ) -> datetime | None:
        """Retrieve and calculate the next run for a schedule."""
        schedule = self._schedule_service.get_schedule(
            schedule_id,
        )

        if schedule is None:
            raise ValueError(
                f"Schedule {schedule_id} does not exist."
            )

        return self.calculate_next_run(
            schedule=schedule,
            current_time=current_time,
        )

    def get_due_schedule_count(
        self,
        current_time: datetime | None = None,
    ) -> int:
        """Return the number of schedules currently due."""
        return len(
            self.get_due_schedules(
                current_time=current_time,
            )
        )