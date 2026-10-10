"""
Project : Email Automation Toolkit
Project ID : 032

Attachment Service
"""

from __future__ import annotations

import mimetypes
from pathlib import Path

from src.models.attachment import Attachment


class AttachmentService:
    """Manage and validate email attachment files."""

    def create_attachment(
        self,
        file_path: Path,
    ) -> Attachment:
        """Create an attachment model from an existing file."""
        resolved_path = file_path.expanduser().resolve()

        self._validate_file(resolved_path)

        mime_type = self._detect_mime_type(resolved_path)
        file_size = resolved_path.stat().st_size

        return Attachment(
            file_path=resolved_path,
            file_name=resolved_path.name,
            mime_type=mime_type,
            file_size=file_size,
        )

    def create_attachments(
        self,
        file_paths: list[Path],
    ) -> list[Attachment]:
        """Create attachment models for multiple files."""
        return [
            self.create_attachment(file_path)
            for file_path in file_paths
        ]

    def validate_attachment(
        self,
        attachment: Attachment,
    ) -> None:
        """Validate that an attachment remains available and accessible."""
        self._validate_file(attachment.file_path)

        if attachment.file_size < 0:
            raise ValueError(
                f"Invalid attachment size: {attachment.file_path}"
            )

        if not attachment.mime_type.strip():
            raise ValueError(
                f"Attachment MIME type is empty: "
                f"{attachment.file_path}"
            )

    @staticmethod
    def _validate_file(file_path: Path) -> None:
        """Validate that a path identifies a readable file."""
        if not file_path.exists():
            raise FileNotFoundError(
                f"Attachment file not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Attachment path is not a file: {file_path}"
            )

        try:
            with file_path.open("rb") as attachment_file:
                attachment_file.read(1)
        except OSError as exc:
            raise OSError(
                f"Attachment file cannot be accessed: {file_path}"
            ) from exc

    @staticmethod
    def _detect_mime_type(file_path: Path) -> str:
        """Determine the MIME type of an attachment file."""
        mime_type, _ = mimetypes.guess_type(file_path.name)

        if mime_type:
            return mime_type

        return "application/octet-stream"