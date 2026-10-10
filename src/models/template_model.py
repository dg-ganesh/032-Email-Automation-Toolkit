"""
Project : Email Automation Toolkit
Project ID : 032

Email Template Model
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateModel:
    """Represent the definition and source locations of an email template."""

    name: str
    html_path: Path
    text_path: Path
    subject_template: str

    @property
    def has_html_template(self) -> bool:
        """Return whether the HTML template file exists."""
        return self.html_path.is_file()

    @property
    def has_text_template(self) -> bool:
        """Return whether the plain-text template file exists."""
        return self.text_path.is_file()