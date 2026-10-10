"""
Project : Email Automation Toolkit
Project ID : 032

Delivery Tracker
"""

from __future__ import annotations

from src.models.delivery_result import DeliveryResult


class DeliveryTracker:
    """Track delivery outcomes and determine retry eligibility."""

    def __init__(
        self,
        max_attempts: int = 3,
    ) -> None:
        if max_attempts < 1:
            raise ValueError(
                "Maximum delivery attempts must be at least 1."
            )

        self._max_attempts = max_attempts

    @property
    def max_attempts(self) -> int:
        """Return the configured maximum number of attempts."""
        return self._max_attempts

    def should_retry(
        self,
        result: DeliveryResult,
    ) -> bool:
        """Determine whether a failed delivery can be retried."""
        if not result.is_failure:
            return False

        return result.attempt_number < self._max_attempts

    def next_attempt_number(
        self,
        result: DeliveryResult,
    ) -> int:
        """Return the next delivery attempt number."""
        if not self.should_retry(result):
            raise ValueError(
                "No further delivery attempt is permitted."
            )

        return result.attempt_number + 1

    def get_status(
        self,
        result: DeliveryResult,
    ) -> str:
        """Return the normalized delivery status."""
        status = result.status.strip().upper()

        if status not in {
            "READY",
            "SUCCESS",
            "FAILED",
        }:
            raise ValueError(
                f"Unsupported delivery status: {result.status}"
            )

        return status

    def summarize(
        self,
        result: DeliveryResult,
    ) -> str:
        """Return a concise operational delivery summary."""
        status = self.get_status(result)

        if status == "SUCCESS":
            return (
                f"Delivery successful on attempt "
                f"{result.attempt_number}."
            )

        if status == "FAILED":
            if self.should_retry(result):
                return (
                    f"Delivery failed on attempt "
                    f"{result.attempt_number}; "
                    f"retry permitted."
                )

            return (
                f"Delivery failed on attempt "
                f"{result.attempt_number}; "
                f"maximum attempts reached."
            )

        return "Delivery is ready for processing."