"""
Project : Email Automation Toolkit
Project ID : 032

Application Configuration
"""

from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------------------------
# Project Identity
# ---------------------------------------------------------------------------

PROJECT_ID = "032"
PROJECT_NAME = "Email Automation Toolkit"
APPLICATION_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
LOGS_DIR = PROJECT_ROOT / "logs"
TESTS_DIR = PROJECT_ROOT / "tests"
RELEASES_DIR = PROJECT_ROOT / "releases"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"


# ---------------------------------------------------------------------------
# Asset Paths
# ---------------------------------------------------------------------------

TEMPLATES_DIR = ASSETS_DIR / "templates"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"


# ---------------------------------------------------------------------------
# Data Paths
# ---------------------------------------------------------------------------

INPUT_DATA_DIR = DATA_DIR / "input"
OUTPUT_DATA_DIR = DATA_DIR / "output"
SAMPLES_DATA_DIR = DATA_DIR / "samples"


# ---------------------------------------------------------------------------
# Runtime Paths
# ---------------------------------------------------------------------------

EXECUTION_REPORT_PATH = LOGS_DIR / "execution_report.txt"
DEBUG_LOG_PATH = LOGS_DIR / "debug.log"
APPLICATION_LOG_PATH = LOGS_DIR / "application.log"


# ---------------------------------------------------------------------------
# Application Defaults
# ---------------------------------------------------------------------------

DEFAULT_TEMPLATE_NAME = "welcome_email"
DEFAULT_OUTPUT_HTML_NAME = "generated_email.html"
DEFAULT_OUTPUT_TEXT_NAME = "generated_email.txt"


def ensure_project_directories() -> None:
    """Create runtime and project directories required by the application."""
    directories = (
        ASSETS_DIR,
        TEMPLATES_DIR,
        ICONS_DIR,
        IMAGES_DIR,
        FONTS_DIR,
        DATA_DIR,
        INPUT_DATA_DIR,
        OUTPUT_DATA_DIR,
        SAMPLES_DATA_DIR,
        DOCS_DIR,
        LOGS_DIR,
        TESTS_DIR,
        RELEASES_DIR,
        BUILD_DIR,
        DIST_DIR,
    )

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)