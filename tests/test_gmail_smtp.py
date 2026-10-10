"""
Project : Email Automation Toolkit
Project ID : 032

Gmail SMTP Integration Test
"""

from __future__ import annotations

from pathlib import Path

from src.config import DATA_DIR
from src.models.email_job import EmailJob
from src.models.email_message import EmailMessage
from src.services.config_service import ConfigService
from src.services.mime_service import MIMEMessageService
from src.services.smtp_service import SMTPService


SMTP_CONFIG_PATH = DATA_DIR / "input" / "smtp_config.json"

TEST_RECIPIENT = "dg.ganesh@gmail.com"


def build_test_email(sender: str) -> EmailJob:
    """Build the controlled Gmail integration test email."""
    email_message = EmailMessage(
        subject="Project 032 - Gmail SMTP Integration Test",
        sender=sender,
        recipients=[TEST_RECIPIENT],
        html_body=(
            "<html>"
            "<body>"
            "<h2>Project 032 Gmail Integration Test</h2>"
            "<p>This is a real email sent by the "
            "Project 032 Email Automation Toolkit.</p>"
            "<p>The message confirms that Gmail SMTP "
            "authentication and delivery are working.</p>"
            "</body>"
            "</html>"
        ),
        text_body=(
            "Project 032 Gmail Integration Test\n\n"
            "This is a real email sent by the "
            "Project 032 Email Automation Toolkit.\n\n"
            "The message confirms that Gmail SMTP "
            "authentication and delivery are working."
        ),
    )

    return EmailJob(
        email_message=email_message,
        template_name="gmail_integration_test",
    )


def run_gmail_test() -> None:
    """Execute the real Gmail SMTP integration test."""
    print("Project 032 - Gmail SMTP Integration Test")
    print()
    print(f"SMTP configuration: {SMTP_CONFIG_PATH}")
    print(f"Recipient: {TEST_RECIPIENT}")
    print()

    if not SMTP_CONFIG_PATH.is_file():
        raise FileNotFoundError(
            "SMTP configuration file was not found: "
            f"{SMTP_CONFIG_PATH}"
        )

    config_service = ConfigService()

    smtp_config = config_service.load_smtp_config(
        config_path=SMTP_CONFIG_PATH,
    )

    config_service.validate_config(
        smtp_config,
    )

    print("SMTP configuration validation ..... PASS")
    print(f"SMTP host ........................ {smtp_config.host}")
    print(f"SMTP port ........................ {smtp_config.port}")
    print(f"STARTTLS .......................... {smtp_config.use_tls}")
    print(f"SSL ............................... {smtp_config.use_ssl}")
    print()

    if smtp_config.host != "smtp.gmail.com":
        raise ValueError(
            "Gmail integration test requires smtp.gmail.com "
            "as the configured SMTP host."
        )

    if smtp_config.port != 587:
        raise ValueError(
            "Gmail STARTTLS integration test requires "
            "SMTP port 587."
        )

    if not smtp_config.use_tls:
        raise ValueError(
            "Gmail STARTTLS integration test requires "
            "use_tls=true."
        )

    if smtp_config.use_ssl:
        raise ValueError(
            "Gmail STARTTLS integration test requires "
            "use_ssl=false."
        )

    print("Gmail SMTP configuration .......... PASS")

    email_job = build_test_email(
        sender=smtp_config.username,
    )

    mime_service = MIMEMessageService()

    mime_message = mime_service.build_message(
        email_job=email_job,
    )

    print("MIME message construction ......... PASS")

    if mime_message["Subject"] != (
        "Project 032 - Gmail SMTP Integration Test"
    ):
        raise RuntimeError(
            "MIME subject verification failed."
        )

    if mime_message["From"] != smtp_config.username:
        raise RuntimeError(
            "MIME sender does not match the configured "
            "Gmail account."
        )

    if TEST_RECIPIENT not in mime_message["To"]:
        raise RuntimeError(
            "MIME recipient does not contain the expected "
            "Gmail address."
        )

    smtp_service = SMTPService(
        smtp_config=smtp_config,
    )

    print("Testing Gmail SMTP authentication ...")

    smtp_service.test_connection()

    print("Gmail SMTP authentication .......... PASS")

    print()
    print("Sending real test email ............")

    smtp_service.send(
        message=mime_message,
    )

    print("Gmail SMTP delivery ................ PASS")
    print()
    print("Gmail integration test completed successfully.")
    print()
    print(
        "Check the recipient inbox for the "
        "'Project 032 - Gmail SMTP Integration Test' email."
    )


def main() -> None:
    """Start the Gmail SMTP integration test."""
    try:
        run_gmail_test()
    except Exception as exc:
        print()
        print("Gmail integration test ............. FAIL")
        print(f"Error: {exc}")
        raise


if __name__ == "__main__":
    main()