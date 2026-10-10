"""
Project : Email Automation Toolkit
Project ID : 032

SMTP Configuration Model
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SMTPConfig:
    """Store validated SMTP connection configuration."""

    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    timeout_seconds: int = 30

    @property
    def requires_authentication(self) -> bool:
        """Return whether SMTP authentication credentials are configured."""
        return bool(
            self.username.strip()
            or self.password.strip()
        )

    @property
    def uses_encryption(self) -> bool:
        """Return whether TLS or SSL encryption is configured."""
        return self.use_tls or self.use_ssl

    @property
    def provider_endpoint(self) -> str:
        """Return the SMTP host and port as a display endpoint."""
        return f"{self.host.strip()}:{self.port}"