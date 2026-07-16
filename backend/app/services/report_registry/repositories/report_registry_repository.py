from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.report_registry import (
    ReportRegistry,
)

from app.services.report_registry.models import (
    RegisteredReport,
    ReportStatus,
)


# ==========================================================
# Repository
# ==========================================================

class ReportRegistryRepository:
    """
    Canonical persistence layer for the
    institutional Report Registry.

    This is the only component permitted to
    read or write ReportRegistry records.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

    # ======================================================
    # Create
    # ======================================================

    def create(
        self,
        *,
        report: RegisteredReport,
        report_title: str,
        report_version: str = "1.0",
        claim_id: int | None = None,
        generated_by: int | None = None,
    ) -> ReportRegistry:

        record = ReportRegistry(

            report_id=report.report_id,

            report_type=report.report_type.value,

            report_title=report_title,

            report_version=report_version,

            workspace_id=report.workspace_id,

            claim_id=claim_id,

            generated_by=generated_by,

            status=report.status.value,

            verification_url=report.verification_url,

            storage_key=report.storage_key,

            file_name=report.file_name,

            sha256=report.sha256,

            file_size=report.file_size,

            metadata_json=report.metadata,

        )

        self.db.add(
            record,
        )

        self.db.commit()

        self.db.refresh(
            record,
        )

        return record

    # ======================================================
    # Lookup
    # ======================================================

    def get_by_report_id(
        self,
        report_id: str,
    ) -> ReportRegistry | None:

        return (

            self.db.query(
                ReportRegistry,
            )

            .filter(

                ReportRegistry.report_id == report_id,

            )

            .first()

        )

    def get_workspace_reports(
        self,
        workspace_id: int,
    ) -> list[ReportRegistry]:

        return (

            self.db.query(
                ReportRegistry,
            )

            .filter(

                ReportRegistry.workspace_id == workspace_id,

            )

            .order_by(

                ReportRegistry.generated_at.desc(),

            )

            .all()

        )

    # ======================================================
    # Status
    # ======================================================

    def mark_verified(
        self,
        report_id: str,
    ) -> None:

        report = self.get_by_report_id(
            report_id,
        )

        if report is None:
            return

        report.status = ReportStatus.VERIFIED.value

        self.db.commit()

    def mark_revoked(
        self,
        report_id: str,
    ) -> None:

        report = self.get_by_report_id(
            report_id,
        )

        if report is None:
            return

        report.status = ReportStatus.REVOKED.value

        self.db.commit()

    # ======================================================
    # Downloads
    # ======================================================

    def register_download(
        self,
        report_id: str,
    ) -> None:

        report = self.get_by_report_id(
            report_id,
        )

        if report is None:
            return

        report.download_count += 1

        report.last_downloaded_at = datetime.utcnow()

        self.db.commit()

    # ======================================================
    # Utility
    # ======================================================

    def exists(
        self,
        report_id: str,
    ) -> bool:

        return (

            self.get_by_report_id(
                report_id,
            )

            is not None

        )