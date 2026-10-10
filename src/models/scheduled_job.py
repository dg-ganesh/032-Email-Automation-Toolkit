"""
Project : Email Automation Toolkit
Project ID : 032

Scheduled Job Model
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.models.schedule import Schedule


@dataclass(frozen=True)
class ScheduledJob:
    """
    Represents an email job configured for scheduled execution.
    """

    scheduled_job_id: int | None
    email_job_id: int
    schedule: Schedule
    status: str = "SCHEDULED"
    last_executed_at: datetime | None = None
    execution_count: int = 0

    def __post_init__(self) -> None:
        status = self.status.strip().upper()

        allowed_statuses = {
            "SCHEDULED",
            "RUNNING",
            "COMPLETED",
            "FAILED",
            "CANCELLED",
        }

        if status not in allowed_statuses:
            raise ValueError(
                "Unsupported scheduled job status: "
                f"{self.status}"
            )

        if self.status != status:
            object.__setattr__(
                self,
                "status",
                status,
            )

        if (
            self.scheduled_job_id is not None
            and self.scheduled_job_id <= 0
        ):
            raise ValueError(
                "Scheduled job ID must be greater than zero."
            )

        if self.email_job_id <= 0:
            raise ValueError(
                "Email job ID must be greater than zero."
            )

        if not isinstance(self.schedule, Schedule):
            raise TypeError(
                "Scheduled job must contain a Schedule instance."
            )

        if self.execution_count < 0:
            raise ValueError(
                "Execution count cannot be negative."
            )

        if self.execution_count == 0 and self.last_executed_at is not None:
            raise ValueError(
                "Last execution time cannot be set when "
                "execution count is zero."
            )

    @property
    def is_active(self) -> bool:
        """Return True when the underlying schedule is active."""
        return self.schedule.is_active

    @property
    def is_one_time(self) -> bool:
        """Return True when the job has a one-time schedule."""
        return self.schedule.is_one_time

    @property
    def is_recurring(self) -> bool:
        """Return True when the job has a recurring schedule."""
        return self.schedule.is_recurring

    @property
    def is_completed(self) -> bool:
        """Return True when the scheduled job is completed."""
        return self.status == "COMPLETED"

    @property
    def is_failed(self) -> bool:
        """Return True when the scheduled job has failed."""
        return self.status == "FAILED"

    @property
    def is_cancelled(self) -> bool:
        """Return True when the scheduled job is cancelled."""
        return self.status == "CANCELLED"

    @property
    def can_execute(self) -> bool:
        """
        Return True when the scheduled job is eligible
        for execution.
        """
        if not self.is_active:
            return False

        if self.status in {"RUNNING", "CANCELLED"}:
            return False

        if self.is_one_time and self.is_completed:
            return False

        return True

    def mark_running(self) -> "ScheduledJob":
        """Return a copy marked as currently running."""
        if not self.can_execute:
            raise ValueError(
                "Scheduled job cannot be marked as running "
                "in its current state."
            )

        return ScheduledJob(
            scheduled_job_id=self.scheduled_job_id,
            email_job_id=self.email_job_id,
            schedule=self.schedule,
            status="RUNNING",
            last_executed_at=self.last_executed_at,
            execution_count=self.execution_count,
        )

    def mark_completed(
        self,
        executed_at: datetime,
    ) -> "ScheduledJob":
        """Return a copy marked as successfully completed."""
        if not isinstance(executed_at, datetime):
            raise TypeError(
                "Execution time must be a datetime value."
            )

        return ScheduledJob(
            scheduled_job_id=self.scheduled_job_id,
            email_job_id=self.email_job_id,
            schedule=self.schedule,
            status="COMPLETED",
            last_executed_at=executed_at,
            execution_count=self.execution_count + 1,
        )

    def mark_failed(
        self,
        executed_at: datetime,
    ) -> "ScheduledJob":
        """Return a copy marked as failed."""
        if not isinstance(executed_at, datetime):
            raise TypeError(
                "Execution time must be a datetime value."
            )

        return ScheduledJob(
            scheduled_job_id=self.scheduled_job_id,
            email_job_id=self.email_job_id,
            schedule=self.schedule,
            status="FAILED",
            last_executed_at=executed_at,
            execution_count=self.execution_count + 1,
        )

    def cancel(self) -> "ScheduledJob":
        """Return a copy marked as cancelled."""
        return ScheduledJob(
            scheduled_job_id=self.scheduled_job_id,
            email_job_id=self.email_job_id,
            schedule=self.schedule.deactivate(),
            status="CANCELLED",
            last_executed_at=self.last_executed_at,
            execution_count=self.execution_count,
        )