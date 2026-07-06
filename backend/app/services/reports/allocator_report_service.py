from app.models.claim_schema import (
    ClaimSchema,
)

from app.models.review_statement import (
    ReviewStatement,
)

from app.services.metrics_service import (
    get_workspace_trade_metrics,
)

from app.services.verification.verification_service import (
    get_workspace_verification_metrics,
)


def build_allocator_report_payload(
    workspace_id: int,
    db,
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    reviews = (
        db.query(ReviewStatement)
        .filter(
            ReviewStatement.workspace_id
            == workspace_id
        )
        .all()
    )

    workspace_verification = (
        get_workspace_verification_metrics(
            db=db,
            workspace_id=workspace_id,
        )
    )

    from app.services.verification.verification_service import (
        get_workspace_claim_verification_certificates,
    )

    workspace_certificates = (
        get_workspace_claim_verification_certificates(
            db=db,
            workspace_id=workspace_id,
        )
    )

    metrics = (
        get_workspace_trade_metrics(
            db,
            workspace_id,
        )
    )

    gross_profit = float(
        metrics.get(
            "gross_profit",
            0,
        ) or 0
    )

    gross_loss = abs(
        float(
            metrics.get(
                "gross_loss",
                0,
            ) or 0
        )
    )

    wins = int(
        metrics.get(
            "wins",
            0,
        ) or 0
    )

    losses = int(
        metrics.get(
            "losses",
            0,
        ) or 0
    )

    average_win = round(
        gross_profit / wins,
        2,
    ) if wins else 0

    average_loss = round(
        gross_loss / losses,
        2,
    ) if losses else 0

    payoff_ratio = round(
        average_win / average_loss,
        2,
    ) if average_loss else 0

    loss_rate = round(
        100 -
        float(
            metrics.get(
                "win_rate",
                0,
            ) or 0
        ),
        2,
    )

    net_profit = round(
        float(
            metrics.get(
                "total_pnl",
                0,
            ) or 0
        ),
        2,
    )

    locked_claims = len(
        [
            c
            for c in claims
            if (
                c.status or ""
            ).lower()
            == "locked"
        ]
    )

    review_count = len(reviews)

    average_rating = (
        round(
            sum(
                r.rating or 0
                for r in reviews
            )
            / review_count,
            2,
        )
        if review_count
        else 0
    )

    trust_score = (
        workspace_verification.network.percentage
    )

    integrity_score = (
        workspace_verification
            .integrity
            .percentage
    )

    evidence_score = (
        workspace_verification
            .evidence
            .percentage
    )

    verification_score = (
        workspace_verification
            .average_verification_score
    )

    allocator_score = round(
        (
            trust_score * 0.25
            + integrity_score * 0.25
            + evidence_score * 0.25
            + verification_score * 0.25
        ),
        2,
    )

    # ==========================================
    # INSTITUTIONAL BANDS
    # ==========================================

    if metrics["profit_factor"] >= 2:
        performance_band = "STRONG"
    elif metrics["profit_factor"] >= 1.2:
        performance_band = "MODERATE"
    else:
        performance_band = "WEAK"


    if metrics["max_drawdown"] <= 10:
        risk_band = "LOW"
    elif metrics["max_drawdown"] <= 20:
        risk_band = "MODERATE"
    else:
        risk_band = "HIGH"


    if verification_score >= 80:
        verification_band = "STRONG"
    elif verification_score >= 50:
        verification_band = "MODERATE"
    else:
        verification_band = "WEAK"


    if integrity_score >= 90:
        integrity_band = "STRONG"
    elif integrity_score >= 70:
        integrity_band = "MODERATE"
    else:
        integrity_band = "WEAK"


    locked_ratio = (
        round(
            (locked_claims / len(claims)) * 100,
            2,
        )
        if len(claims)
        else 0
    )

    if locked_ratio >= 80:
        governance_band = "STRONG"
    elif locked_ratio >= 50:
        governance_band = "MODERATE"
    else:
        governance_band = "WEAK"

    score_breakdown = {
        "trust_score": trust_score,
        "integrity_score": integrity_score,
        "evidence_score": evidence_score,
        "verification_score": verification_score,
    }

    if allocator_score >= 90:
        allocator_band = (
            "INSTITUTIONAL GRADE"
        )

    elif allocator_score >= 80:
        allocator_band = (
            "ALLOCATOR READY"
        )

    elif allocator_score >= 70:
        allocator_band = (
            "MONITORING"
        )

    else:
        allocator_band = (
            "HIGH REVIEW"
        )

    if allocator_score >= 85:
        verdict = (
            "CAPITAL ALLOCATION ELIGIBLE"
        )

    elif allocator_score >= 70:
        verdict = (
            "CONDITIONAL REVIEW"
        )

    else:
        verdict = (
            "NOT RECOMMENDED"
        )

    allocator_risks = []

    if metrics["max_drawdown"] > 20:
        allocator_risks.append(
            "drawdown_present"
        )

    if integrity_score < 80:
        allocator_risks.append(
            "integrity_monitoring_required"
        )

    if evidence_score < 80:
        allocator_risks.append(
            "evidence_quality_monitoring"
        )

    if allocator_score < 70:
        allocator_risks.append(
            "allocator_threshold_not_met"
        )

    allocation_capacity = (
        "APPROVED"
        if allocator_score >= 85
        else "REVIEW"
        if allocator_score >= 70
        else "REJECTED"
    )

    operational_risk = "LOW"

    if integrity_score < 80:
        operational_risk = "MODERATE"

    if integrity_score < 60:
        operational_risk = "HIGH"

    #
    # NOTE
    #
    # verification_certificate is the canonical
    # institutional verification object.
    #
    # The legacy verification/evidence/integrity/
    # governance/trust sections remain temporarily
    # for backward compatibility while report
    # modules migrate to TVS.
    #

    return {

        #
        # Workspace TVS Objects
        #

        "workspace_verification":
            workspace_verification,

        "workspace_certificates":
            workspace_certificates,

        #
        # Temporary compatibility alias
        #
        # Will be removed once every report
        # consumes the workspace objects directly.
        #

        "verification_certificate":
            workspace_verification,

        "allocator_assessment": {

            "allocator_score":
                allocator_score,

            "allocator_band":
                allocator_band,

            "verdict":
                verdict,

            "allocation_capacity":
                allocation_capacity,
        },

        "performance": {

            "trade_count":
                metrics["trade_count"],

            "total_pnl":
                metrics["total_pnl"],

            "net_profit": f"${net_profit:,.2f}",

            "gross_profit": f"${gross_profit:,.2f}",

            "gross_loss": f"${gross_loss:,.2f}",

            "profit_factor": f"{metrics['profit_factor']:.2f}",

            "expectancy": f"{metrics['expectancy']:.2f}",

            "win_rate": f"{metrics['win_rate']:.2f}%",

            "loss_rate": f"{loss_rate:.2f}%",

            "average_win": f"${average_win:,.2f}",

            "average_loss": f"${average_loss:,.2f}",

            "payoff_ratio": f"{payoff_ratio:.2f}",

            "performance_band":
                performance_band,
        },

        "risk": {

            "operational_risk":
                operational_risk,

            "max_drawdown":
                f"{metrics.get('peak_to_trough_drawdown_units', metrics.get('max_drawdown', 0)):,.2f}",

            "max_drawdown_pct":
                f"{metrics.get('max_drawdown_pct', 0):.2f}%",

            "wins":
                wins,

            "losses":
                losses,

            "recovery_factor":
                f"{metrics.get('recovery_factor', 0):.2f}",

            "payoff_ratio":
                f"{payoff_ratio:.2f}",

            "risk_band":
                risk_band,
        },

        "verification": {

            "coverage":
                verification_score,

            "verification_score":
                verification_score,

            "verification_band":
                verification_band,

            "verified":
                workspace_verification.claim_count,

            "broker_verified":
                workspace_verification.claim_count,

            "self_reported":
                0,

            "verified_ratio":
                100.0 if workspace_verification.claim_count else 0,

            "broker_verified_ratio":
                100.0 if workspace_verification.claim_count else 0,

            "self_reported_ratio":
                0.0,
        },

        "trust": {

            "trust_score":
                trust_score,

            "network_score":
                workspace_verification
                    .network
                    .percentage,

            "trust_band":
                workspace_verification
                    .network
                    .status,
        },

        "evidence": {

            "quality_score":
                evidence_score,

            "quality_band":
                workspace_verification
                    .evidence
                    .status,

            "tier_distribution": {},

            "overview": {},

            "verification": {},

            "evidence_count":
                workspace_verification.claim_count,

            "coverage":
                verification_score,

            "reliability":
                workspace_verification
                    .evidence
                    .percentage,

            "protection":
                workspace_verification
                    .evidence
                    .percentage,

            "tier_1_count": 0,

            "tier_2_count": 0,

            "tier_3_count": 0,
        },

        "integrity": {

            "integrity_score":
                integrity_score,

            "open_findings": 0,

            "resolved_findings": 0,

            "scanner_status": {},

            "severity": {},

            "recent_findings": [],

            "critical_findings": 0,

            "high_findings": 0,

            "warning_findings": 0,

            "fatal_findings": 0,

            "integrity_band":
                workspace_verification
                    .integrity
                    .status,
        },

        "governance": {

            "claims":
                len(claims),

            "locked_claims":
                locked_claims,

            "review_count":
                review_count,

            "average_rating":
                average_rating,

            "locked_ratio":
                locked_ratio,

            "governance_band":
                governance_band,

            "governance_score":
                workspace_verification
                    .governance
                    .percentage,

            "transparency_score":
                workspace_verification
                    .transparency
                    .percentage,

            "stability_score":
                workspace_verification
                    .stability
                    .percentage,

            "network_score":
                workspace_verification
                    .network
                    .percentage,

            "published_claims":
                len(
                    [
                        c
                        for c in claims
                        if (
                            c.status or ""
                        ).lower()
                        == "published"
                    ]
                ),

            "verified_claims":
                len(
                    [
                        c
                        for c in claims
                        if (
                            c.status or ""
                        ).lower()
                        == "verified"
                    ]
                ),

            "draft_claims":
                len(
                    [
                        c
                        for c in claims
                        if (
                            c.status or ""
                        ).lower()
                        == "draft"
                    ]
                ),
        },

        "executive_summary": {

            "allocator_score":
                allocator_score,

            "allocator_band":
                allocator_band,

            "verdict":
                verdict,

            "performance_band":
                performance_band,

            "risk_band":
                risk_band,

            "verification_band":
                verification_band,

            "integrity_band":
                integrity_band,

            "governance_band":
                governance_band,
        },

        "performance_band":
            performance_band,

        "risk_band":
            risk_band,

        "verification_band":
            verification_band,

        "integrity_band":
            integrity_band,

        "governance_band":
            governance_band,

        "allocator_risks": {

            "count":
                len(
                    allocator_risks
                ),

            "items":
                allocator_risks,
        },

        "allocator_scorecard": {
            "allocator_score": allocator_score,
            "trust_score": trust_score,
            "integrity_score": integrity_score,
            "evidence_score": evidence_score,
            "verification_score": verification_score,
        },

        "score_breakdown":
            score_breakdown,

        "resolution_metrics": {

            "total_findings": 0,

            "open_findings": 0,

            "resolved_findings": 0,

            "resolution_rate": 0,
        },

        "allocator_decision": {

            "capacity":

                (
                    "APPROVED"
                    if allocator_score >= 85
                    else "CONDITIONAL"
                    if allocator_score >= 70
                    else "REJECTED"
                ),

            "verdict":
                verdict,

            "institutional_ready":
                allocator_score >= 85,

            "review_required":
                allocator_score < 85,
        },

        "report_metadata": {

            "report_type":
                "ALLOCATOR",

            "workspace_id":
                workspace_id,

            "version":
                "2.0",

            "verification_engine":
                "TVS",

            "verification_source":
                "verification_certificate",
        },

        "verification_links": {

            "allocator_route":
                f"/reports/workspace/{workspace_id}/allocator",

            "verification_route":
                f"/reports/workspace/{workspace_id}/verification",

            "audit_route":
                f"/reports/workspace/{workspace_id}/audit",
        },
    }