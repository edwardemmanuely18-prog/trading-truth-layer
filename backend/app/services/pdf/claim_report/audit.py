from __future__ import annotations

"""
Trading Truth Layer
Claim Report

Audit & Verification Lineage

Institutional audit trail supporting a
verified trading claim.

Consumes only the canonical Claim Report
context produced by TVS.

No verification logic exists here.
"""

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_metric_block,
    build_callout,
    build_narrative,
    build_findings,
)

from app.services.pdf.common.institutional_tables import (
    build_metric_table,
)


# ==========================================================
# PRESENTATION HELPERS
# ==========================================================

def score(component):

    return (
        f"{component.earned_points} / "
        f"{component.maximum_points}"
    )


def confidence(value):

    if value is None:
        return "Not Available"

    value = float(value)

    if value <= 1:
        value *= 100

    return f"{value:.1f}%"


# ==========================================================
# AUDIT
# ==========================================================

def build_audit_section(
    context: dict,
):

    verification = context["verification"]

    certificate = context["certificate"]

    metadata = context["metadata"]

    lifecycle = context["lifecycle"]

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Audit Trail & Verification Lineage",

            build_narrative(

                """
                Institutional confidence depends not only
                on the verification outcome but also on
                the ability to independently reproduce
                that outcome.

                The Trading Verification System (TVS)
                maintains immutable audit records,
                certificate identities and verification
                lineage that establish complete
                traceability from submitted evidence to
                the issued Verification Certificate.

                This section summarizes the audit
                artifacts supporting independent
                institutional review.
                """

            ),

        )

    )

    #
    # Audit Dashboard
    #

    rows = [

        [
            "Audit Metric",
            "Value",
        ],

        [
            "Claim ID",
            verification.claim_schema_id,
        ],

        [
            "Workspace ID",
            verification.workspace_id,
        ],

        [
            "Certificate Version",
            certificate.identity.certificate_version,
        ],

        [
            "TVS Version",
            certificate.identity.tvs_version,
        ],

    ]

    story.extend(

        build_metric_block(

            "Verification Audit Trail",

            build_metric_table(
                rows,
            ),

        )

    )

    #
    # Certificate Identity
    #

    certificate_rows = [

        [
            "Certificate Identity",
            "Value",
        ],

        [
            "Certificate Version",
            certificate.identity.certificate_version,
        ],

        [
            "TVS Version",
            certificate.identity.tvs_version,
        ],

        [
            "Certificate Hash",
            context["metadata"]["certificate_hash"],
        ],

        [
            "Claim Hash",
            context["metadata"]["claim_hash"],
        ],

    ]

    story.extend(

        build_metric_block(

            "Certificate Identity",

            build_metric_table(
                certificate_rows,
            ),

        )

    )

    #
    # Verification Timeline
    #

    timeline_rows = [

        [
            "Lifecycle",
            "Timestamp",
        ],

        [
            "Verified",
            lifecycle.get("verified_at"),
        ],

        [
            "Published",
            lifecycle.get("published_at"),
        ],

        [
            "Locked",
            lifecycle.get("locked_at"),
        ],

    ]

    story.extend(

        build_metric_block(

            "Verification Timeline",

            build_metric_table(
                timeline_rows,
            ),

        )

    )

    lineage_rows = [

        [
            "Verification Lineage",
            "Reference",
        ],

        [
            "Certificate Version",
            certificate.identity.certificate_version,
        ],

        [
            "TVS Version",
            certificate.identity.tvs_version,
        ],

        [
            "Certificate Hash",
            context["metadata"]["certificate_hash"],
        ],

        [
            "Claim Hash",
            context["metadata"]["claim_hash"],
        ],

    ]

    story.extend(

        build_metric_block(

            "Verification Lineage",

            build_metric_table(
                lineage_rows,
            ),

        )

    )

    story.extend(

        build_findings(

            [

                "The Verification Certificate maintains complete lineage through immutable certificate identifiers.",

                "Lifecycle timestamps support independent reconstruction of the verification process.",

                "Version-controlled certificate metadata ensures long-term reproducibility of institutional verification.",

                "Audit artifacts provide an independent foundation for institutional due diligence.",

            ],

            title="Audit Findings",

        )

    )

    return story