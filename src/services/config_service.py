"""
Project : Email Automation Toolkit
Project ID : 032

SMTP Configuration Service
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.smtp_config import SMTPConfig


class ConfigService:
    """Load and validate external SMTP configuration."""

    REQUIRED_FIELDS = {
        "host",
        "port",
        "username",
        "password",
    }

    def load_smtp_config(
        self,
        config_path: Path,
    ) -> SMTPConfig:
        """Load SMTP configuration from a JSON file."""
        if not config_path.is_file():
            raise FileNotFoundError(
                f"SMTP configuration file not found: {config_path}"
            )

        try:
            configuration = json.loads(
                config_path.read_text(
                    encoding="utf-8",
                )
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in SMTP configuration: {config_path}"
            ) from exc

        if not isinstance(configuration, dict):
            raise ValueError(
                "SMTP configuration must contain a JSON object."
            )

        smtp_configuration = configuration.get("smtp")

        if not isinstance(smtp_configuration, dict):
            raise ValueError(
                "SMTP configuration must contain an 'smtp' object."
            )

        self._validate_required_fields(
            smtp_configuration,
        )

        return SMTPConfig(
            host=self._read_string(
                smtp_configuration,
                "host",
            ),
            port=self._read_integer(
                smtp_configuration,
                "port",
            ),
            username=self._read_string(
                smtp_configuration,
                "username",
            ),
            password=self._read_string(
                smtp_configuration,
                "password",
            ),
            use_tls=self._read_boolean(
                smtp_configuration,
                "use_tls",
                default=True,
            ),
            use_ssl=self._read_boolean(
                smtp_configuration,
                "use_ssl",
                default=False,
            ),
            timeout_seconds=self._read_integer(
                smtp_configuration,
                "timeout_seconds",
                default=30,
            ),
        )

    @classmethod
    def validate_config(
        cls,
        config: SMTPConfig,
    ) -> None:
        """Validate an SMTP configuration model."""
        if not config.host.strip():
            raise ValueError(
                "SMTP host cannot be empty."
            )

        if not 1 <= config.port <= 65535:
            raise ValueError(
                "SMTP port must be between 1 and 65535."
            )

        if config.use_tls and config.use_ssl:
            raise ValueError(
                "SMTP configuration cannot use TLS and SSL "
                "simultaneously."
            )

        if config.timeout_seconds <= 0:
            raise ValueError(
                "SMTP timeout must be greater than zero."
            )

        if config.requires_authentication:
            if not config.username.strip():
                raise ValueError(
                    "SMTP username cannot be empty when "
                    "authentication is configured."
                )

            if not config.password.strip():
                raise ValueError(
                    "SMTP password cannot be empty when "
                    "authentication is configured."
                )

    @classmethod
    def _validate_required_fields(
        cls,
        configuration: dict[str, Any],
    ) -> None:
        """Validate that mandatory configuration fields exist."""
        missing_fields = sorted(
            cls.REQUIRED_FIELDS.difference(
                configuration.keys()
            )
        )

        if missing_fields:
            raise ValueError(
                "Missing SMTP configuration fields: "
                + ", ".join(missing_fields)
            )

    @staticmethod
    def _read_string(
        configuration: dict[str, Any],
        field_name: str,
    ) -> str:
        """Read a required string configuration value."""
        value = configuration.get(field_name)

        if not isinstance(value, str):
            raise ValueError(
                f"SMTP configuration field '{field_name}' "
                "must be a string."
            )

        return value

    @staticmethod
    def _read_integer(
        configuration: dict[str, Any],
        field_name: str,
        default: int | None = None,
    ) -> int:
        """Read an integer configuration value."""
        value = configuration.get(
            field_name,
            default,
        )

        if isinstance(value, bool) or not isinstance(
            value,
            int,
        ):
            raise ValueError(
                f"SMTP configuration field '{field_name}' "
                "must be an integer."
            )

        return value

    @staticmethod
    def _read_boolean(
        configuration: dict[str, Any],
        field_name: str,
        default: bool,
    ) -> bool:
        """Read a boolean configuration value."""
        value = configuration.get(
            field_name,
            default,
        )

        if not isinstance(value, bool):
            raise ValueError(
                f"SMTP configuration field '{field_name}' "
                "must be a boolean."
            )

        return value