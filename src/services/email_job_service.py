"""
Project : Email Automation Toolkit
Project ID : 032

Email Job Service
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.models.attachment import Attachment
from src.models.email_job import EmailJob
from src.models.email_message import EmailMessage
from src.models.recipient import Recipient
from src.services.database_service import DatabaseService


class EmailJobService:
    """
    Persists and reconstructs complete EmailJob objects.
    """

    def __init__(
        self,
        database_service: DatabaseService,
    ) -> None:
        self._database = database_service

    def initialize(self) -> None:
        """Create persistence structures for complete email jobs."""
        self._database.execute(
            """
            CREATE TABLE IF NOT EXISTS email_job_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_job_id INTEGER NOT NULL,
                recipient_id INTEGER NOT NULL,
                recipient_type TEXT NOT NULL DEFAULT 'TO',
                FOREIGN KEY (email_job_id)
                    REFERENCES email_jobs(id),
                FOREIGN KEY (recipient_id)
                    REFERENCES recipients(id)
            )
            """
        )

        self._ensure_recipient_type_column()

        self._database.execute(
            """
            CREATE TABLE IF NOT EXISTS email_job_content (
                email_job_id INTEGER PRIMARY KEY,
                html_body TEXT NOT NULL,
                text_body TEXT NOT NULL,
                FOREIGN KEY (email_job_id)
                    REFERENCES email_jobs(id)
            )
            """
        )

        self._database.execute(
            """
            CREATE TABLE IF NOT EXISTS email_job_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_job_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                FOREIGN KEY (email_job_id)
                    REFERENCES email_jobs(id)
            )
            """
        )

    def _ensure_recipient_type_column(self) -> None:
        """
        Add recipient_type to an existing database when required.

        Existing recipient relationships are treated as TO recipients
        because the previous schema did not preserve recipient type.
        """
        columns = self._database.fetch_all(
            """
            PRAGMA table_info(email_job_recipients)
            """
        )

        column_names = {
            row["name"]
            for row in columns
        }

        if "recipient_type" not in column_names:
            self._database.execute(
                """
                ALTER TABLE email_job_recipients
                ADD COLUMN recipient_type TEXT
                NOT NULL
                DEFAULT 'TO'
                """
            )

    def save_email_job(
        self,
        email_job: EmailJob,
    ) -> int:
        """Persist a complete email job and return its ID."""
        if email_job.job_id is not None:
            raise ValueError(
                "A new email job cannot already have an ID."
            )

        email_job_id = self._database.execute(
            """
            INSERT INTO email_jobs (
                subject,
                sender,
                template_name,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                email_job.email_message.subject,
                email_job.email_message.sender,
                email_job.template_name,
                email_job.status,
                email_job.created_at.isoformat(
                    timespec="seconds"
                ),
            ),
        )

        if not email_job_id:
            raise RuntimeError(
                "Email job persistence did not return an ID."
            )

        self._save_content(
            email_job_id=email_job_id,
            email_job=email_job,
        )

        self._save_recipients(
            email_job_id=email_job_id,
            email_job=email_job,
        )

        self._save_attachments(
            email_job_id=email_job_id,
            email_job=email_job,
        )

        return email_job_id

    def get_email_job(
        self,
        email_job_id: int,
    ) -> EmailJob | None:
        """Retrieve and reconstruct a complete email job."""
        if email_job_id <= 0:
            raise ValueError(
                "Email job ID must be greater than zero."
            )

        row = self._database.fetch_one(
            """
            SELECT
                id,
                subject,
                sender,
                template_name,
                status,
                created_at
            FROM email_jobs
            WHERE id = ?
            """,
            (email_job_id,),
        )

        if row is None:
            return None

        content_row = self._database.fetch_one(
            """
            SELECT
                html_body,
                text_body
            FROM email_job_content
            WHERE email_job_id = ?
            """,
            (email_job_id,),
        )

        if content_row is None:
            raise RuntimeError(
                "Email job content is missing."
            )

        recipient_relationships = (
            self._load_recipient_relationships(
                email_job_id,
            )
        )

        attachments = self._load_attachments(
            email_job_id,
        )

        email_message = EmailMessage(
            subject=row["subject"],
            sender=row["sender"],
            recipients=[
                relationship["recipient"].email
                for relationship in recipient_relationships
                if (
                    relationship["recipient"].is_active
                    and relationship["recipient_type"] == "TO"
                )
            ],
            cc_recipients=[
                relationship["recipient"].email
                for relationship in recipient_relationships
                if (
                    relationship["recipient"].is_active
                    and relationship["recipient_type"] == "CC"
                )
            ],
            bcc_recipients=[
                relationship["recipient"].email
                for relationship in recipient_relationships
                if (
                    relationship["recipient"].is_active
                    and relationship["recipient_type"] == "BCC"
                )
            ],
            html_body=content_row["html_body"],
            text_body=content_row["text_body"],
        )

        return EmailJob(
            email_message=email_message,
            attachments=attachments,
            template_name=row["template_name"],
            job_id=row["id"],
            status=row["status"],
            created_at=datetime.fromisoformat(
                row["created_at"],
            ),
        )

    def _save_content(
        self,
        email_job_id: int,
        email_job: EmailJob,
    ) -> None:
        """Persist rendered email content."""
        self._database.execute(
            """
            INSERT INTO email_job_content (
                email_job_id,
                html_body,
                text_body
            )
            VALUES (?, ?, ?)
            """,
            (
                email_job_id,
                email_job.email_message.html_body,
                email_job.email_message.text_body,
            ),
        )

    def _save_recipients(
        self,
        email_job_id: int,
        email_job: EmailJob,
    ) -> None:
        """Persist recipient relationships with their recipient types."""
        recipient_groups = (
            (
                "TO",
                email_job.email_message.recipients,
            ),
            (
                "CC",
                email_job.email_message.cc_recipients,
            ),
            (
                "BCC",
                email_job.email_message.bcc_recipients,
            ),
        )

        total_recipients = sum(
            len(emails)
            for _, emails in recipient_groups
        )

        if total_recipients == 0:
            raise ValueError(
                "Email job must contain at least one "
                "persisted recipient."
            )

        for recipient_type, recipient_emails in recipient_groups:
            recipient_ids = self._find_recipient_ids(
                recipient_emails,
            )

            for recipient_id in recipient_ids:
                self._database.execute(
                    """
                    INSERT INTO email_job_recipients (
                        email_job_id,
                        recipient_id,
                        recipient_type
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        email_job_id,
                        recipient_id,
                        recipient_type,
                    ),
                )

    def _save_attachments(
        self,
        email_job_id: int,
        email_job: EmailJob,
    ) -> None:
        """Persist attachment metadata."""
        for attachment in email_job.attachments:
            self._database.execute(
                """
                INSERT INTO email_job_attachments (
                    email_job_id,
                    file_path,
                    file_name,
                    mime_type,
                    file_size
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    email_job_id,
                    str(attachment.file_path),
                    attachment.file_name,
                    attachment.mime_type,
                    attachment.file_size,
                ),
            )

    def _find_recipient_ids(
        self,
        recipient_emails: list[str],
    ) -> list[int]:
        """Resolve recipient email addresses to database IDs."""
        recipient_ids: list[int] = []

        for email in recipient_emails:
            row = self._database.fetch_one(
                """
                SELECT id
                FROM recipients
                WHERE LOWER(email) = LOWER(?)
                """,
                (email,),
            )

            if row is None:
                raise ValueError(
                    f"Recipient does not exist: {email}"
                )

            recipient_ids.append(row["id"])

        return recipient_ids

    def _load_recipient_relationships(
        self,
        email_job_id: int,
    ) -> list[dict[str, object]]:
        """
        Load recipient relationships with recipient types.
        """
        rows = self._database.fetch_all(
            """
            SELECT
                r.id,
                r.name,
                r.email,
                r.is_active,
                ejr.recipient_type
            FROM recipients r
            INNER JOIN email_job_recipients ejr
                ON r.id = ejr.recipient_id
            WHERE ejr.email_job_id = ?
            ORDER BY ejr.id
            """,
            (email_job_id,),
        )

        relationships: list[dict[str, object]] = []

        for row in rows:
            recipient_type = str(
                row["recipient_type"] or "TO"
            ).upper()

            if recipient_type not in {
                "TO",
                "CC",
                "BCC",
            }:
                raise RuntimeError(
                    "Invalid recipient type persisted for "
                    f"email job {email_job_id}: "
                    f"{recipient_type}"
                )

            relationships.append(
                {
                    "recipient": Recipient(
                        name=row["name"],
                        email=row["email"],
                        is_active=bool(row["is_active"]),
                        recipient_id=row["id"],
                    ),
                    "recipient_type": recipient_type,
                }
            )

        return relationships

    def _load_attachments(
        self,
        email_job_id: int,
    ) -> list[Attachment]:
        """Load attachment metadata associated with an email job."""
        rows = self._database.fetch_all(
            """
            SELECT
                id,
                file_path,
                file_name,
                mime_type,
                file_size
            FROM email_job_attachments
            WHERE email_job_id = ?
            ORDER BY id
            """,
            (email_job_id,),
        )

        return [
            Attachment(
                file_path=Path(row["file_path"]),
                file_name=row["file_name"],
                mime_type=row["mime_type"],
                file_size=row["file_size"],
                attachment_id=row["id"],
            )
            for row in rows
        ]