"""
Project : Email Automation Toolkit
Project ID : 032

Email Template Service
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from src.models.template_model import TemplateModel


class TemplateService:
    """Load and render Jinja2 email templates."""

    def __init__(self, templates_directory: Path) -> None:
        """Initialize the template service with the template directory."""
        self._templates_directory = templates_directory

        self._environment = Environment(
            loader=FileSystemLoader(templates_directory),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def list_template_names(self) -> list[str]:
        """Return template names that have both HTML and text files."""
        if not self._templates_directory.is_dir():
            raise FileNotFoundError(
                f"Templates directory not found: {self._templates_directory}"
            )

        html_names = {
            path.stem
            for path in self._templates_directory.glob("*.html")
            if path.is_file()
        }
        text_names = {
            path.stem
            for path in self._templates_directory.glob("*.txt")
            if path.is_file()
        }

        return sorted(html_names & text_names)

    def create_template_model(
        self,
        name: str,
        subject_template: str,
    ) -> TemplateModel:
        """Create a template model by selecting a template file pair."""
        clean_name = name.strip()

        if not clean_name:
            raise ValueError("Template name must not be empty.")

        if Path(clean_name).name != clean_name:
            raise ValueError("Template name must be a file stem, not a path.")

        if clean_name not in self.list_template_names():
            raise FileNotFoundError(
                f"No matching HTML and text template pair found: {clean_name}"
            )

        return TemplateModel(
            name=clean_name,
            html_path=self._templates_directory / f"{clean_name}.html",
            text_path=self._templates_directory / f"{clean_name}.txt",
            subject_template=subject_template,
        )

    def load_template(self, template: TemplateModel) -> TemplateModel:
        """Validate that the configured template files are available."""
        if not template.html_path.is_file():
            raise FileNotFoundError(
                f"HTML template not found: {template.html_path}"
            )

        if not template.text_path.is_file():
            raise FileNotFoundError(
                f"Plain-text template not found: {template.text_path}"
            )

        return template

    def render_html(
        self,
        template: TemplateModel,
        data: dict[str, Any],
    ) -> str:
        """Render the HTML template using the supplied data."""
        self.load_template(template)

        template_name = template.html_path.name

        try:
            jinja_template = self._environment.get_template(template_name)
        except TemplateNotFound as exc:
            raise FileNotFoundError(
                f"Unable to load HTML template: {template_name}"
            ) from exc

        return jinja_template.render(**data)

    def render_text(
        self,
        template: TemplateModel,
        data: dict[str, Any],
    ) -> str:
        """Render the plain-text template using the supplied data."""
        self.load_template(template)

        template_name = template.text_path.name

        try:
            jinja_template = self._environment.get_template(template_name)
        except TemplateNotFound as exc:
            raise FileNotFoundError(
                f"Unable to load plain-text template: {template_name}"
            ) from exc

        return jinja_template.render(**data)

    def render_subject(
        self,
        template: TemplateModel,
        data: dict[str, Any],
    ) -> str:
        """Render the email subject using the template subject definition."""
        subject_template = self._environment.from_string(
            template.subject_template
        )

        return subject_template.render(**data)