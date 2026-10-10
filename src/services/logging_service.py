"""
Project : Email Automation Toolkit
Project ID : 032

Execution Logging Service
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from time import perf_counter


class LoggingService:
    """Manage runtime execution reporting for the application."""

    def __init__(
        self,
        report_path: Path,
        application_version: str,
    ) -> None:
        """Initialize the logging service."""
        self._report_path = report_path
        self._application_version = application_version
        self._start_time = perf_counter()
        self._execution_start = datetime.now()
        self._checkpoints: list[str] = []
        self._status = "PASS"
        self._last_successful_checkpoint = "None"
        self._error_information = "None"

    def start_execution(self) -> None:
        """Initialize the execution report."""
        self._start_time = perf_counter()
        self._execution_start = datetime.now()
        self._checkpoints.clear()
        self._status = "PASS"
        self._last_successful_checkpoint = "None"
        self._error_information = "None"

        self._write_report()

    def record_checkpoint(
        self,
        checkpoint: str,
        status: str = "PASS",
    ) -> None:
        """Record an execution checkpoint."""
        normalized_status = status.strip().upper()

        if normalized_status not in {"PASS", "FAIL"}:
            raise ValueError(
                "Checkpoint status must be either 'PASS' or 'FAIL'."
            )

        entry = f"{checkpoint}: {normalized_status}"
        self._checkpoints.append(entry)

        if normalized_status == "PASS":
            self._last_successful_checkpoint = checkpoint
        else:
            self._status = "FAIL"

        self._write_report()

    def record_error(self, error: Exception | str) -> None:
        """Record execution error information."""
        self._status = "FAIL"
        self._error_information = str(error)
        self._write_report()

    def complete_execution(self, status: str = "PASS") -> None:
        """Complete the execution report."""
        normalized_status = status.strip().upper()

        if normalized_status not in {"PASS", "FAIL"}:
            raise ValueError(
                "Execution status must be either 'PASS' or 'FAIL'."
            )

        if normalized_status == "FAIL":
            self._status = "FAIL"

        self._write_report()

    def _write_report(self) -> None:
        """Write the current execution state to the report file."""
        self._report_path.parent.mkdir(parents=True, exist_ok=True)

        execution_duration = perf_counter() - self._start_time

        report_lines = [
            "Project 032 - Email Automation Toolkit",
            "Execution Report",
            "=" * 50,
            f"Application Version: {self._application_version}",
            (
                "Execution Start Time: "
                f"{self._execution_start.strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            (
                "Execution Duration: "
                f"{execution_duration:.3f} seconds"
            ),
            f"Status: {self._status}",
            (
                "Last Successful Checkpoint: "
                f"{self._last_successful_checkpoint}"
            ),
            "",
            "Completed Execution Checkpoints:",
        ]

        if self._checkpoints:
            report_lines.extend(
                f"- {checkpoint}" for checkpoint in self._checkpoints
            )
        else:
            report_lines.append("- None")

        report_lines.extend(
            [
                "",
                f"Error Information: {self._error_information}",
                "=" * 50,
            ]
        )

        self._report_path.write_text(
            "\n".join(report_lines) + "\n",
            encoding="utf-8",
        )