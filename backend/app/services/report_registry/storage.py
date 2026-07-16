from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# ==========================================================
# Configuration
# ==========================================================

#
# Canonical report storage directory.
#
# This implementation stores reports locally.
# It can later be replaced by S3, R2 or Azure
# without changing the Report Registry API.
#

REPORT_STORAGE_ROOT = (
    Path("storage")
    / "reports"
)


# ==========================================================
# Storage Result
# ==========================================================

@dataclass(slots=True)
class StoredReport:

    storage_key: str

    file_name: str

    absolute_path: Path


# ==========================================================
# Helpers
# ==========================================================

def ensure_report_storage() -> None:

    REPORT_STORAGE_ROOT.mkdir(

        parents=True,

        exist_ok=True,

    )


# ==========================================================
# Public API
# ==========================================================

def store_report(
    *,
    report_id: str,
    file_name: str,
    pdf_bytes: bytes,
) -> StoredReport:
    """
    Stores a generated institutional report.

    The caller does not need to know whether
    storage is local, S3 or any future backend.
    """

    ensure_report_storage()

    storage_key = (
        f"{report_id}.pdf"
    )

    path = (
        REPORT_STORAGE_ROOT
        / storage_key
    )

    path.write_bytes(
        pdf_bytes,
    )

    return StoredReport(

        storage_key=storage_key,

        file_name=file_name,

        absolute_path=path,

    )


def load_report(
    *,
    storage_key: str,
) -> bytes:
    """
    Loads a stored report.
    """

    path = (
        REPORT_STORAGE_ROOT
        / storage_key
    )

    return path.read_bytes()


def report_exists(
    *,
    storage_key: str,
) -> bool:
    """
    Returns whether a stored report exists.
    """

    return (
        REPORT_STORAGE_ROOT
        / storage_key
    ).exists()