"""
Project : Email Automation Toolkit
Project ID : 032

Delivery Service
"""

from __future__ import annotations

from datetime import datetime

from src.models.email_message import EmailMessage

from src.core.email_validator import EmailValidator
from src.models.delivery_result import DeliveryResult
from src.models.email_job import EmailJob
from src.services.mime_service import MIMEMessageService
from src.services.smtp_service import SMTPService


class DeliveryService:
    """Coordinate validation, MIME construction, and SMTP delivery."""

    def __init__(
        self,
        smtp_service: SMTPService,
        mime_service: MIMEMessageService,
        email_validator: EmailValidator,
    ) -> None:
        self._smtp_service = smtp_service
        self._mime_service = mime_service
        self._email_validator = email_validator

    def deliver(
        self,
        email_job: EmailJob,
        attempt_number: int = 1,
    ) -> DeliveryResult:
        """Deliver an email job and return the delivery result."""
        attempted_at = datetime.now()

        if attempt_number < 1:
            raise ValueError(
                "Delivery attempt number must be at least 1."
            )

        try:
            self._email_validator.validate(
                email_job,
            )

            mime_message = self._mime_service.build_message(
                email_job,
            )

            self._smtp_service.send(
                mime_message,
            )

            return DeliveryResult(
                status="SUCCESS",
                attempted_at=attempted_at,
                attempt_number=attempt_number,
                smtp_response="Email accepted by SMTP transport.",
            )

        except Exception as exc:
            return DeliveryResult(
                status="FAILED",
                attempted_at=attempted_at,
                attempt_number=attempt_number,
                error_message=str(exc),
            )

    def deliver_individually(
        self,
        email_job: EmailJob,
        attempt_number: int = 1,
    ) -> list[DeliveryResult]:
        """
        Send one separate email per To recipient.

        Each individual message contains only that recipient in To.
        CC and BCC lists are preserved for each message, if supplied.
        Results are returned in the same order as the To recipients.
        """
        recipients = list(email_job.email_message.recipients)

        if not recipients:
            return [
                DeliveryResult(
                    status="FAILED",
                    attempted_at=datetime.now(),
                    attempt_number=attempt_number,
                    error_message=(
                        "Individual delivery requires at least one To recipient."
                    ),
                )
            ]

        results: list[DeliveryResult] = []

        for recipient in recipients:
            individual_message = EmailMessage(
                subject=email_job.email_message.subject,
                sender=email_job.email_message.sender,
                recipients=[recipient],
                cc_recipients=list(
                    email_job.email_message.cc_recipients
                ),
                bcc_recipients=list(
                    email_job.email_message.bcc_recipients
                ),
                html_body=email_job.email_message.html_body,
                text_body=email_job.email_message.text_body,
            )

            individual_job = EmailJob(
                email_message=individual_message,
                attachments=list(email_job.attachments),
                template_name=email_job.template_name,
                job_id=email_job.job_id,
                status=email_job.status,
                created_at=email_job.created_at,
            )

            results.append(
                self.deliver(
                    email_job=individual_job,
                    attempt_number=attempt_number,
                )
            )

        return results
