
"""
Project : Email Automation Toolkit
Project ID : 032

Database Service
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator


class DatabaseService:
    """Manage SQLite persistence for the Email Automation Toolkit."""

    def __init__(self, database_path: Path) -> None:
        """Initialize the database service with a SQLite database path."""
        self._database_path = Path(database_path)

    def initialize(self) -> None:
        """Create the database and required application tables."""
        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS recipient_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS recipient_group_members (
                    group_id INTEGER NOT NULL,
                    recipient_id INTEGER NOT NULL,
                    PRIMARY KEY (group_id, recipient_id),
                    FOREIGN KEY (group_id)
                        REFERENCES recipient_groups(id),
                    FOREIGN KEY (recipient_id)
                        REFERENCES recipients(id)
                );

                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    html_path TEXT NOT NULL,
                    text_path TEXT NOT NULL,
                    subject_template TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS email_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def execute(
        self,
        query: str,
        parameters: Iterable[Any] = (),
    ) -> int:
        """Execute a SQL statement and return its last inserted row ID."""
        with self._connect() as connection:
            cursor = connection.execute(
                query,
                tuple(parameters),
            )
            connection.commit()
            return cursor.lastrowid

    def execute_many(
        self,
        query: str,
        parameter_sets: Iterable[Iterable[Any]],
    ) -> None:
        """Execute a SQL statement for multiple parameter sets."""
        with self._connect() as connection:
            connection.executemany(
                query,
                [tuple(parameters) for parameters in parameter_sets],
            )
            connection.commit()

    def fetch_one(
        self,
        query: str,
        parameters: Iterable[Any] = (),
    ) -> sqlite3.Row | None:
        """Return the first row produced by a query."""
        with self._connect() as connection:
            cursor = connection.execute(
                query,
                tuple(parameters),
            )
            return cursor.fetchone()

    def fetch_all(
        self,
        query: str,
        parameters: Iterable[Any] = (),
    ) -> list[sqlite3.Row]:
        """Return all rows produced by a query."""
        with self._connect() as connection:
            cursor = connection.execute(
                query,
                tuple(parameters),
            )
            return cursor.fetchall()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Create, configure, and reliably close a SQLite connection."""
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        try:
            yield connection
        finally:
            connection.close()
