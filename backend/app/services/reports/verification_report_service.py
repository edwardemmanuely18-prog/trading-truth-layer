from app.models.claim_schema import (
    ClaimSchema,
)

from app.services.evidence_analytics_service import (
    build_evidence_analytics,
)

from app.services.integrity.integrity_dashboard_service import (
    build_integrity_dashboard,
)

from app.api.routes.claim_schemas import (
    build_public_trust_profile_for_workspace,
)


def build_verification_report_payload(
    workspace_id: int,
    db,
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .order_by(
            ClaimSchema.id.desc()
        )
        .all()
    )

    trust_profile = (
        build_public_trust_profile_for_workspace(
            workspace_id,
            db,
        )
    )

    evidence = (
        build_evidence_analytics(
            db,
            workspace_id,
        )
    )

    integrity = (
        build_integrity_dashboard(
            db,
            workspace_id,
        )
    )

    verification_chain = []

    verified_claims = 0
    published_claims = 0
    locked_claims = 0

    for claim in claims:

        status = (
            claim.status or ""
        ).lower()

        if status == "verified":
            verified_claims += 1

        elif status == "published":
            published_claims += 1

        elif status == "locked":
            locked_claims += 1

        verification_chain.append(
            {
                "claim_id":
                    claim.id,

                "claim_name":
                    claim.name,

                "status":
                    claim.status,

                "claim_hash":
                    claim.claim_hash,

                "scope_hash":
                    claim.scope_hash,

                "lifecycle_hash":
                    claim.lifecycle_hash,

                "trade_set_hash":
                    claim.locked_trade_set_hash,

                "evidence_snapshot_hash":
                    claim.evidence_snapshot_hash,

                "version":
                    claim.version_number,

                "visibility":
                    claim.visibility,

                "verified_at":
                    claim.verified_at,

                "published_at":
                    claim.published_at,

                "locked_at":
                    claim.locked_at,
            }
        )

    total_claims = len(claims)

    verification_coverage = (
        round(
            (
                (
                    verified_claims
                    + published_claims
                    + locked_claims
                )
                / total_claims
            )
            * 100,
            2,
        )
        if total_claims
        else 0
    )

    verification_risks = []

    if integrity["open_findings"] > 0:
        verification_risks.append(
            "open_integrity_findings"
        )

    if evidence["quality"]["score"] < 80:
        verification_risks.append(
            "low_evidence_quality"
        )

    if verification_coverage < 100:
        verification_risks.append(
            "incomplete_verification"
        )

    return {

        "summary": {

            "claims":
                total_claims,

            "verified_claims":
                verified_claims,

            "published_claims":
                published_claims,

            "locked_claims":
                locked_claims,

            "verification_coverage":
                verification_coverage,
        },

        "trust": {

            "trust_score":
                trust_profile.get(
                    "average_trust_score",
                    0,
                ),

            "network_score":
                trust_profile.get(
                    "average_network_score",
                    0,
                ),

            "trust_band":
                trust_profile.get(
                    "trust_profile_band",
                    "unknown",
                ),
        },

        "evidence": {

            "coverage":
                evidence["overview"][
                    "coverage"
                ],

            "quality_score":
                evidence["quality"][
                    "score"
                ],

            "quality_band":
                evidence["quality"][
                    "band"
                ],

            "tier_distribution":
                evidence["tiers"],

            "verification_distribution":
                evidence[
                    "verification"
                ],
        },

        "integrity": {

            "integrity_score":
                integrity[
                    "integrity_score"
                ],

            "open_findings":
                integrity[
                    "open_findings"
                ],

            "resolved_findings":
                integrity[
                    "resolved_findings"
                ],

            "severity":
                integrity[
                    "severity"
                ],
        },

        "verification_chain":
            verification_chain,

        "verification_risks": {

            "count":
                len(
                    verification_risks
                ),

            "items":
                verification_risks,
        },

        "report_metadata": {

            "report_type":
                "VERIFICATION",

            "workspace_id":
                workspace_id,

            "version":
                "1.0",
        },

        "verification_links": {

            "verification_route":
                f"/reports/workspace/{workspace_id}/verification",

            "audit_route":
                f"/reports/workspace/{workspace_id}/audit",
        },
    }