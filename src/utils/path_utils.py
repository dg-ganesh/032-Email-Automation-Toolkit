"""
Project : Email Automation Toolkit
Project ID : 032

Path Utilities
"""

from __future__ import annotations

from pathlib import Path


def ensure_directory(directory: Path) -> Path:
    """Create a directory if it does not already exist."""
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_file_parent(file_path: Path) -> Path:
    """Ensure that the parent directory of a file exists."""
    return ensure_directory(file_path.parent)


def file_exists(file_path: Path) -> bool:
    """Return whether the supplied path points to a file."""
    return file_path.is_file()


def directory_exists(directory: Path) -> bool:
    """Return whether the supplied path points to a directory."""
    return directory.is_dir()


def resolve_path(path: Path) -> Path:
    """Return the absolute, normalized representation of a path."""
    return path.expanduser().resolve()


def get_file_name(file_path: Path) -> str:
    """Return the filename component of a path."""
    return file_path.name