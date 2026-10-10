"""
Project : Email Automation Toolkit
Project ID : 032

Scheduled Execution Service
"""

from __future__ import annotations

from src.models.delivery_result import DeliveryResult
from src.services.delivery_history_service import (
    DeliveryHistoryService,
)
from src.services.delivery_service import DeliveryService
from src.services.email_job_service import EmailJobService


class ScheduledExecutionService:
    """
    Executes scheduled email jobs through the existing
    delivery infrastructure.
    """

    def __init__(
        self,
        email_job_service: EmailJobService,
        delivery_service: DeliveryService,
        delivery_history_service: DeliveryHistoryService,
    ) -> None:
        self._email_job_service = email_job_service
        self._delivery_service = delivery_service
        self._delivery_history_service = (
            delivery_history_service
        )

    def execute(
        self,
        email_job_id: int,
        attempt_number: int = 1,
    ) -> DeliveryResult:
        """
        Load and execute an existing email job.
        """
        if email_job_id <= 0:
            raise ValueError(
                "Email job ID must be greater than zero."
            )

        if attempt_number < 1:
            raise ValueError(
                "Delivery attempt number must be at least 1."
            )

        email_job = self._email_job_service.get_email_job(
            email_job_id,
        )

        if email_job is None:
            raise ValueError(
                f"Email job {email_job_id} does not exist."
            )

        result = self._delivery_service.deliver(
            email_job=email_job,
            attempt_number=attempt_number,
        )

        self._delivery_history_service.record_delivery(
            email_job_id=email_job_id,
            result=result,
        )

        return result

    def execute_with_retry(
        self,
        email_job_id: int,
        max_attempts: int = 3,
    ) -> DeliveryResult:
        """
        Execute an email job and retry failed deliveries
        up to the configured maximum number of attempts.
        """
        if email_job_id <= 0:
            raise ValueError(
                "Email job ID must be greater than zero."
            )

        if max_attempts < 1:
            raise ValueError(
                "Maximum delivery attempts must be at least 1."
            )

        latest_result: DeliveryResult | None = None

        for attempt_number in range(
            1,
            max_attempts + 1,
        ):
            latest_result = self.execute(
                email_job_id=email_job_id,
                attempt_number=attempt_number,
            )

            if latest_result.is_success:
                return latest_result

        if latest_result is None:
            raise RuntimeError(
                "Scheduled execution did not produce a result."
            )

        return latest_result

    def get_latest_result(
        self,
        email_job_id: int,
    ) -> DeliveryResult | None:
        """Return the latest recorded delivery result."""
        if email_job_id <= 0:
            raise ValueError(
                "Email job ID must be greater than zero."
            )

        return self._delivery_history_service.get_latest_delivery(
            email_job_id=email_job_id,
        )