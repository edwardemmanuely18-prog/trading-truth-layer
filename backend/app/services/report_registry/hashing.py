from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


# ==========================================================
# Hash Result
# ==========================================================

@dataclass(slots=True)
class ReportHash:

    sha256: str

    file_size: int


# ==========================================================
# Public API
# ==========================================================

def compute_report_hash(
    pdf_bytes: bytes,
) -> ReportHash:
    """
    Computes the canonical fingerprint of a
    generated institutional report.

    Every report (Claim, Allocator,
    Investigation, Executive, etc.)
    should use this function.
    """

    digest = sha256(
        pdf_bytes,
    ).hexdigest()

    return ReportHash(

        sha256=digest,

        file_size=len(pdf_bytes),

    )