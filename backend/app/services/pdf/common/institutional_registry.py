from __future__ import annotations

"""
Trading Truth Layer
Institutional Report Registry

This registry defines every institutional report
available within Trading Truth Layer.

No report should hardcode its identity,
classification or branding.

Every report imports its metadata from here.
"""

from dataclasses import dataclass


# ==========================================================
# Report Definition
# ==========================================================


@dataclass(frozen=True, slots=True)
class InstitutionalReportDefinition:

    slug: str

    title: str

    subtitle: str

    short_name: str

    classification: str

    system: str

    version: str

    watermark: str

    qr_label: str


# ==========================================================
# Canonical Registry
# ==========================================================


REPORTS: dict[str, InstitutionalReportDefinition] = {

    "claim":

        InstitutionalReportDefinition(

            slug="claim",

            title="Institutional Claim Report",

            subtitle="TVS Canonical",

            short_name="Claim Report",

            classification="Institutional Verification Document",

            system="Trading Verification System (TVS)",

            version="TVS V1",

            watermark="CLAIM",

            qr_label="Verify Claim",

        ),

    "allocator":

        InstitutionalReportDefinition(

            slug="allocator",

            title="Institutional Allocator Report",

            subtitle="Allocator Decision Package",

            short_name="Allocator Report",

            classification="Allocator Due Diligence",

            system="Allocator Engine",

            version="Allocator V1",

            watermark="ALLOCATOR",

            qr_label="Verify Allocator Report",

        ),

    "verification":

        InstitutionalReportDefinition(

            slug="verification",

            title="Institutional Verification Report",

            subtitle="Verification Infrastructure",

            short_name="Verification Report",

            classification="Verification Analysis",

            system="Trading Verification System",

            version="TVS V1",

            watermark="VERIFICATION",

            qr_label="Verify Report",

        ),

    "investigation":

        InstitutionalReportDefinition(

            slug="investigation",

            title="Institutional Investigation Report",

            subtitle="Institutional Investigation System",

            short_name="Investigation Report",

            classification="Institutional Investigation",

            system="Institutional Investigation System",

            version="IIS V1",

            watermark="INVESTIGATION",

            qr_label="Verify Investigation",

        ),

    "audit":

        InstitutionalReportDefinition(

            slug="audit",

            title="Institutional Audit Report",

            subtitle="Governance Infrastructure",

            short_name="Audit Report",

            classification="Audit Evidence",

            system="Audit Engine",

            version="Audit V1",

            watermark="AUDIT",

            qr_label="Verify Audit",

        ),

    "evidence":

        InstitutionalReportDefinition(

            slug="evidence",

            title="Institutional Evidence Report",

            subtitle="Evidence Infrastructure",

            short_name="Evidence Report",

            classification="Evidence Package",

            system="Evidence Engine",

            version="Evidence V1",

            watermark="EVIDENCE",

            qr_label="Verify Evidence",

        ),

    "due_diligence":

        InstitutionalReportDefinition(

            slug="due_diligence",

            title="Institutional Due Diligence Report",

            subtitle="Allocator Decision Package",

            short_name="Due Diligence",

            classification="Allocator Due Diligence",

            system="Institutional Investigation System",

            version="IIS V1",

            watermark="DUE DILIGENCE",

            qr_label="Verify Due Diligence",

        ),

}


# ==========================================================
# Helpers
# ==========================================================


def get_report_definition(
    report_type: str,
) -> InstitutionalReportDefinition:

    try:

        return REPORTS[report_type]

    except KeyError as exc:

        raise ValueError(
            f"Unknown report type '{report_type}'."
        ) from exc


__all__ = [

    "InstitutionalReportDefinition",

    "REPORTS",

    "get_report_definition",

]