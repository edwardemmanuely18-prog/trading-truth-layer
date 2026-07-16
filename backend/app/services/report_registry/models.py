from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ==========================================================
# Report Type
# ==========================================================

class ReportType(str, Enum):

    CLAIM = "CLAIM"

    ALLOCATOR = "ALLOCATOR"

    INVESTIGATION = "INVESTIGATION"

    EXECUTIVE = "EXECUTIVE"


# ==========================================================
# Report Status
# ==========================================================

class ReportStatus(str, Enum):

    RESERVED = "RESERVED"

    GENERATED = "GENERATED"

    VERIFIED = "VERIFIED"

    ARCHIVED = "ARCHIVED"

    REVOKED = "REVOKED"


# ==========================================================
# Registered Report
# ==========================================================

@dataclass(slots=True)
class RegisteredReport:
    """
    Canonical institutional report.

    The same object is used during both phases
    of the report lifecycle.

        Reservation
            ↓
        PDF Rendering
            ↓
        Final Registration

    During reservation only the report identity
    and verification URL are populated.

    During finalization the storage information,
    fingerprint and metadata are completed.
    """

    # ======================================================
    # Identity
    # ======================================================

    report_id: str

    report_type: ReportType

    workspace_id: int

    generated_at: datetime

    status: ReportStatus

    verification_url: str

    # ======================================================
    # Storage
    # ======================================================

    file_name: str = ""

    storage_key: str = ""

    sha256: str = ""

    file_size: int = 0

    # ======================================================
    # Optional Context
    # ======================================================

    claim_id: int | None = None

    report_title: str = ""

    report_version: str = "1.0"

    generated_by: int | None = None

    # ======================================================
    # Metadata
    # ======================================================

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # ======================================================
    # Lifecycle Helpers
    # ======================================================

    @property
    def is_reserved(self) -> bool:

        return self.status is ReportStatus.RESERVED

    @property
    def is_generated(self) -> bool:

        return self.status is ReportStatus.GENERATED

    @property
    def is_finalized(self) -> bool:

        return bool(

            self.sha256
            and self.storage_key
            and self.file_name

        )