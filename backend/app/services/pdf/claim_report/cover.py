from __future__ import annotations

"""
Trading Truth Layer
Institutional Claim Report

Cover Page

Consumes ONLY the canonical Claim Report
context.
"""

from app.services.pdf.common.institutional_cover import (
    build_institutional_cover,
)


# ==========================================================
# COVER
# ==========================================================

def build_cover(
    context: dict,
):

    summary = context["summary"]

    metadata = context["metadata"]

    lifecycle = context["lifecycle"]

    performance = context["performance"]["summary"]

    evidence = context["evidence"]["tier_profile"]

    report = context.get(
        "report",
        {},
    )

    #
    # Canonical Verification URL
    #

    verification_url = metadata.get(
        "verification_url",
    )

    if verification_url:

        if verification_url.startswith("/"):

            verification_url = (
                "https://www.tradingtruthlayer.com"
                + verification_url
            )

    cover = {

        "Claim":
            metadata["claim_name"],

        "Claim ID":
            metadata["claim_schema_id"],

        "Verification Status":
            str(summary["status"]).title(),

        "Verification Score":
            f'{summary["score"]:.1f}/100',

        "Verification Band":
            summary["band"],

        "Verification Tier":
            summary["tier"].replace("tier_", "Tier ").replace("1","I").replace("2","II").replace("3","III"),

        "Primary Evidence":
            evidence.get(
                "primary_tier",
                "Unknown",
            ).replace("tier_", "Tier ").replace("1","I").replace("2","II").replace("3","III"),

        "Evidence Source":
            evidence.get(
                "primary_source",
                "Unknown",
            ),

        "Verified":
            lifecycle["verified_at"],

        "Certificate Version":
            metadata["certificate_version"],

        "TVS Version":
            metadata["tvs_version"],

    }

    #
    # QR code requires the canonical verification URL.
    # Do not display it in the metadata table,
    # but still pass it to the common cover builder.
    #

    if verification_url:

        cover["Verification URL"] = verification_url

    workspace = metadata.get("workspace_name")

    if workspace and workspace != "Not Available":
        cover["Workspace"] = workspace

    notice = (

        "This Institutional Claim Report presents the Trading "
        "Truth Layer assessment of a single verified trading "
        "claim. Historical trading performance is evaluated by "
        "the Trading Performance System (TPS), while evidence "
        "quality, governance, transparency, operational integrity "
        "and verification confidence are independently assessed "
        "by the Trading Verification System (TVS).\n\n"

        "<b>Report Highlights</b><br/><br/>"

        "&bull; Independent Trading Performance System (TPS) assessment.<br/>"
        "&bull; Independent Trading Verification System (TVS) assessment.<br/>"
        "&bull; Evidence provenance and institutional quality review.<br/>"
        "&bull; Governance, transparency and operational integrity assessment.<br/>"
        "&bull; Immutable audit lineage and certificate traceability.<br/>"
        "&bull; Final institutional verification verdict.<br/><br/>"

        "<b>Report Structure</b><br/><br/>"

        "&bull; Executive Summary<br/>"
        "&bull; Trading Performance Assessment<br/>"
        "&bull; Evidence Assessment<br/>"
        "&bull; Trading Verification Assessment<br/>"
        "&bull; Operational Governance<br/>"
        "&bull; Audit Trail & Verification Lineage<br/>"
        "&bull; Institutional Verification Verdict<br/>"
        "&bull; Independent Verification Reference<br/><br/>"

        "<b>Primary Institutional Use Cases</b><br/><br/>"

        "&bull; Capital allocators performing manager due diligence.<br/>"
        "&bull; Investment committees reviewing historical trading performance.<br/>"
        "&bull; Independent auditors validating verification lineage.<br/>"
        "&bull; Counterparties evaluating operational credibility.<br/>"
        "&bull; Brokers and custodians requiring verification evidence.<br/>"
        "&bull; Regulatory and compliance review requiring transparent auditability.<br/><br/>"

        "<b>Institutional Review Principle</b><br/><br/>"

        "All findings presented in this report are produced exclusively "
        "by the canonical TPS and TVS engines. The assessment is fully "
        "traceable through immutable evidence, verification lineage and "
        "certificate metadata, allowing independent institutional review."

    )

    workspace = metadata.get("workspace_name")

    subtitle = f'Claim: {metadata["claim_name"]}'

    if workspace and workspace != "Not Available":

        subtitle += f"\nWorkspace: {workspace}"

    return build_institutional_cover(

        title="Institutional Claim Report",

        subtitle=subtitle,

        score=summary["score"],

        band=summary["band"],

        metadata=cover,

        classification=(
            "Trading Truth Layer "
            "Institutional Verification Document"
        ),

        notice=notice,

    )