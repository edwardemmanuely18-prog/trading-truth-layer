from __future__ import annotations

from app.services.report_registry.models import (
    ReportType,
)


# ==========================================================
# Configuration
# ==========================================================

#
# Canonical public verification endpoint.
#
# Eventually this can move into application
# settings without changing the Report Registry.
#

import os


VERIFY_BASE_URL = os.getenv(

    "REPORT_VERIFY_BASE_URL",

    "http://localhost:8001",

).rstrip("/")


# ==========================================================
# Public API
# ==========================================================

def build_report_verification_url(
    *,
    report_id: str,
) -> str:
    """
    Builds the canonical public verification URL
    for an institutional report.

    Example

        https://verify.tradingtruthlayer.com/report/ABC123
    """

    return (
        f"{VERIFY_BASE_URL}"
        f"/report/{report_id}"
    )


def build_report_download_url(
    *,
    report_id: str,
) -> str:
    """
    Builds the canonical public download URL.

    The QR verification page can expose this
    endpoint so institutions always download the
    registered immutable report.
    """

    return (
        f"{VERIFY_BASE_URL}"
        f"/report/{report_id}/download"
    )


def build_report_api_url(
    *,
    report_id: str,
) -> str:
    """
    Canonical machine-readable endpoint.

    Future integrations (allocators, auditors,
    regulators, API consumers) should consume
    this endpoint rather than parsing PDFs.
    """

    return (
        f"{VERIFY_BASE_URL}"
        f"/api/report/{report_id}"
    )