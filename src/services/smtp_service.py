"""
Project : Email Automation Toolkit
Project ID : 032

SMTP Transport Service
"""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from src.models.smtp_config import SMTPConfig


class SMTPService:
    """Send MIME messages through a configured SMTP server."""

    def __init__(
        self,
        smtp_config: SMTPConfig,
    ) -> None:
        self._config = smtp_config

    def send(
        self,
        message: EmailMessage,
    ) -> None:
        """Connect to the SMTP server and send a MIME message."""
        self._validate_transport_configuration()

        if self._config.use_ssl:
            self._send_using_ssl(message)
            return

        self._send_using_smtp(message)

    def test_connection(self) -> None:
        """Test SMTP connectivity and authentication without sending."""
        self._validate_transport_configuration()

        if self._config.use_ssl:
            self._test_ssl_connection()
            return

        self._test_smtp_connection()

    def _send_using_ssl(
        self,
        message: EmailMessage,
    ) -> None:
        """Send a message using implicit SSL."""
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            host=self._config.host,
            port=self._config.port,
            timeout=self._config.timeout_seconds,
            context=context,
        ) as smtp:
            self._authenticate_if_required(smtp)
            smtp.send_message(message)

    def _send_using_smtp(
        self,
        message: EmailMessage,
    ) -> None:
        """Send a message using standard SMTP with optional STARTTLS."""
        with smtplib.SMTP(
            host=self._config.host,
            port=self._config.port,
            timeout=self._config.timeout_seconds,
        ) as smtp:
            smtp.ehlo()

            if self._config.use_tls:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                smtp.ehlo()

            self._authenticate_if_required(smtp)
            smtp.send_message(message)

    def _test_ssl_connection(self) -> None:
        """Test an implicit SSL SMTP connection."""
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            host=self._config.host,
            port=self._config.port,
            timeout=self._config.timeout_seconds,
            context=context,
        ) as smtp:
            self._authenticate_if_required(smtp)

    def _test_smtp_connection(self) -> None:
        """Test a standard SMTP connection with optional STARTTLS."""
        with smtplib.SMTP(
            host=self._config.host,
            port=self._config.port,
            timeout=self._config.timeout_seconds,
        ) as smtp:
            smtp.ehlo()

            if self._config.use_tls:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                smtp.ehlo()

            self._authenticate_if_required(smtp)

    def _authenticate_if_required(
        self,
        smtp: smtplib.SMTP | smtplib.SMTP_SSL,
    ) -> None:
        """Authenticate when credentials have been configured."""
        if not self._config.requires_authentication:
            return

        smtp.login(
            self._config.username,
            self._config.password,
        )

    def _validate_transport_configuration(self) -> None:
        """Validate SMTP transport mode before opening a connection."""
        if not self._config.host.strip():
            raise ValueError(
                "SMTP host cannot be empty."
            )

        if not 1 <= self._config.port <= 65535:
            raise ValueError(
                "SMTP port must be between 1 and 65535."
            )

        if self._config.use_tls and self._config.use_ssl:
            raise ValueError(
                "SMTP cannot use STARTTLS and implicit SSL "
                "simultaneously."
            )

        if self._config.timeout_seconds <= 0:
            raise ValueError(
                "SMTP timeout must be greater than zero."
            )

        if self._config.requires_authentication:
            if not self._config.username.strip():
                raise ValueError(
                    "SMTP username cannot be empty when "
                    "authentication is configured."
                )

            if not self._config.password.strip():
                raise ValueError(
                    "SMTP password cannot be empty when "
                    "authentication is configured."
                )