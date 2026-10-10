"""
Project : Email Automation Toolkit
Project ID : 032

Attachment Model
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Attachment:
    """Represent a file attachment associated with an email."""

    file_path: Path
    file_name: str
    mime_type: str
    file_size: int
    attachment_id: int | None = None

    @property
    def exists(self) -> bool:
        """Return whether the attachment file currently exists."""
        return self.file_path.is_file()

    @property
    def size_in_kilobytes(self) -> float:
        """Return the attachment size in kilobytes."""
        return self.file_size / 1024

    @property
    def size_in_megabytes(self) -> float:
        """Return the attachment size in megabytes."""
        return self.file_size / (1024 * 1024)