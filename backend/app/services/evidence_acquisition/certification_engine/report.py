"""
Institutional reporting for the Evidence Acquisition
Certification Engine.

Reports convert certification results into portable
TTL Integration Certificates.

The report layer never performs certification.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from .models import (
    CertificationReport,
    CertificationResult,
)


class CertificationReportGenerator:
    """
    Generates institutional certification reports.
    """

    def __init__(
        self,
        generated_by: str = "TTL Certification Engine",
    ) -> None:
        self._generated_by = generated_by

    def generate(
        self,
        results: List[CertificationResult],
    ) -> CertificationReport:
        """
        Generate a certification report.
        """

        return CertificationReport(
            generated_at=datetime.utcnow(),
            generated_by=self._generated_by,
            results=list(results),
        )

    def generate_single(
        self,
        result: CertificationResult,
    ) -> CertificationReport:
        """
        Generate a report for a single provider.
        """

        return self.generate([result])


__all__ = [
    "CertificationReportGenerator",
]