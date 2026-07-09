from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema


# ==========================================================
# CLAIM SNAPSHOT
# ==========================================================

def build_claim_snapshot(
    db: Session,
    claim: ClaimSchema,
):
    """
    Canonical snapshot for one claim.

    This is a read model.

    It does not compute anything itself.

    It simply captures the current state
    produced by the canonical engines.
    """

    return {

        "claim_id": claim.id,

        "workspace_id": claim.workspace_id,

        "list_row":
            build_claim_list_row(
                claim,
                db,
            ),

        "public":
            build_public_claim_payload(
                claim,
                db,
            ),
    }


# ==========================================================
# WORKSPACE SNAPSHOT
# ==========================================================

def build_workspace_snapshot(
    db: Session,
    workspace_id: int,
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .order_by(
            ClaimSchema.id.desc()
        )
        .all()
    )

    claim_count = len(claims)

    usage = get_workspace_usage(
        workspace_id,
        db,
    )

    verified_claims = len([
        c for c in claims
        if c.status == "verified"
    ])

    published_claims = len([
        c for c in claims
        if c.status == "published"
    ])

    locked_claims = len([
        c for c in claims
        if c.status == "locked"
    ])

    trust_coverage = (
        round(
            (
                (published_claims + locked_claims)
                / claim_count
            ) * 100,
            2,
        )
        if claim_count
        else 0
    )

    return {

        "workspace_id": workspace_id,

        "profile":
            build_public_trust_profile_for_workspace(
                workspace_id,
                db,
            ),

        "claim_count": claim_count,

        # ===========================================
        # Executive Health
        # ===========================================

        "health": {

            "score": None,

            "state": "INITIALIZING",

            "integrity_alerts": 0,

        },

        # ===========================================
        # Workflow
        # ===========================================

        "workflow": {

            "evidence_intake":
                claim_count > 0,

            "claim_production":
                claim_count > 0,

            "verification":
                (
                    verified_claims > 0
                    or published_claims > 0
                    or locked_claims > 0
                ),

            "public_trust":
                (
                    published_claims > 0
                    or locked_claims > 0
                ),

        },

        # ===========================================
        # Runtime Services
        # ===========================================

        "services": {

            "evidence_engine":
                "INITIALIZING",

            "verification_engine":
                "INITIALIZING",

            "report_engine":
                "INITIALIZING",

            "governance_engine":
                "INITIALIZING",

            "trust_layer":
                "ACTIVE",

        },

        # ===========================================
        # Capacity
        # ===========================================

        "capacity": {

            "configured_plan":
                usage["effective_plan_code"],

            "trade_capacity":
                usage["trade_limit"],

            "claim_capacity":
                usage["claim_limit"],

            "member_capacity":
                usage["member_limit"],

            "storage_capacity":
                usage["storage_limit_mb"],

        },

        # ===========================================
        # Executive Intelligence
        # ===========================================

        "executive": {

            "verification_stage":
                (
                    "Locked"
                    if locked_claims
                    else
                    "Verified"
                    if verified_claims
                    else
                    "Draft"
                    if claim_count
                    else
                    "Empty"
                ),

            "trust_coverage":
                trust_coverage,

            "public_ready":
                locked_claims > 0,

            "next_action":
                (
                    "Review governed output"
                    if locked_claims
                    else
                    "Continue verification"
                ),

        },

    }