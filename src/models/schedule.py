"""
Project : Email Automation Toolkit
Project ID : 032

Schedule Model
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Schedule:
    """
    Represents a schedule definition for an email workflow.
    """

    schedule_id: int | None
    schedule_type: str
    scheduled_at: datetime
    interval_minutes: int | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        schedule_type = self.schedule_type.strip().upper()

        if schedule_type not in {"ONCE", "RECURRING"}:
            raise ValueError(
                "Schedule type must be ONCE or RECURRING."
            )

        if self.schedule_type != schedule_type:
            object.__setattr__(
                self,
                "schedule_type",
                schedule_type,
            )

        if self.schedule_id is not None and self.schedule_id <= 0:
            raise ValueError(
                "Schedule ID must be greater than zero."
            )

        if not isinstance(self.scheduled_at, datetime):
            raise TypeError(
                "Scheduled time must be a datetime value."
            )

        if schedule_type == "RECURRING":
            if self.interval_minutes is None:
                raise ValueError(
                    "Recurring schedules require an interval."
                )

            if self.interval_minutes <= 0:
                raise ValueError(
                    "Recurring schedule interval must be "
                    "greater than zero."
                )

        if schedule_type == "ONCE" and self.interval_minutes is not None:
            raise ValueError(
                "One-time schedules cannot define a recurring interval."
            )

    @property
    def is_recurring(self) -> bool:
        """Return True when the schedule repeats."""
        return self.schedule_type == "RECURRING"

    @property
    def is_one_time(self) -> bool:
        """Return True when the schedule executes once."""
        return self.schedule_type == "ONCE"

    @property
    def is_due(self) -> bool:
        """
        Return True when the schedule's scheduled time
        has been reached.
        """
        return self.is_active and datetime.now() >= self.scheduled_at

    @property
    def interval_seconds(self) -> int | None:
        """Return the recurring interval in seconds."""
        if self.interval_minutes is None:
            return None

        return self.interval_minutes * 60

    def deactivate(self) -> "Schedule":
        """Return an inactive copy of the schedule."""
        return Schedule(
            schedule_id=self.schedule_id,
            schedule_type=self.schedule_type,
            scheduled_at=self.scheduled_at,
            interval_minutes=self.interval_minutes,
            is_active=False,
        )

    def activate(self) -> "Schedule":
        """Return an active copy of the schedule."""
        return Schedule(
            schedule_id=self.schedule_id,
            schedule_type=self.schedule_type,
            scheduled_at=self.scheduled_at,
            interval_minutes=self.interval_minutes,
            is_active=True,
        )

    def next_run(self) -> datetime | None:
        """
        Calculate the next scheduled execution time.

        One-time schedules do not have a recurring next run.
        """
        if not self.is_recurring:
            return None

        if self.interval_minutes is None:
            return None

        return self.scheduled_at.replace(
            second=self.scheduled_at.second,
            microsecond=self.scheduled_at.microsecond,
        )