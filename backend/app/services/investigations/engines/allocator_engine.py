from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDecision,
    InvestigationDomain,
    InvestigationSeverity,
)


class AllocatorEngine:
    """
    Institutional Allocator Decision Engine.

    This is the final IIS reasoning engine.

    It consumes completed investigation domains and
    produces the institutional decision.

    This engine NEVER:

    - queries the database
    - performs verification
    - performs replay
    - recalculates evidence

    It reasons over completed investigations.
    """

    ENGINE_NAME = "Allocator"

    @classmethod
    def build(
        cls,
        *,
        execution: InvestigationDomain | None = None,
        evidence: InvestigationDomain | None = None,
        governance: InvestigationDomain | None = None,
        broker: InvestigationDomain | None = None,
        synchronization: InvestigationDomain | None = None,
        review: InvestigationDomain | None = None,
        behavior: InvestigationDomain | None = None,
        verification: InvestigationDomain | None = None,
    ) -> InvestigationDecision:

        domains = [
            execution,
            evidence,
            governance,
            broker,
            synchronization,
            review,
            behavior,
            verification,
        ]

        completed = [
            d
            for d in domains
            if d is not None
        ]

        if not completed:

            return InvestigationDecision(
                decision="REJECT",
                confidence=0.0,
                rationale=(
                    "No completed investigation domains were "
                    "available."
                ),
                residual_risk=InvestigationSeverity.CRITICAL,
                required_actions=[
                    "Complete investigation pipeline."
                ],
                metadata={
                    "completed_domains": 0,
                },
            )

        average_confidence = (
            sum(
                domain.confidence
                for domain in completed
            )
            / len(completed)
        )

        required_actions: list[str] = []

        weak_domains: list[str] = []

        domain_breakdown: list[dict[str, Any]] = []

        for domain in completed:

            status = (
                "HEALTHY"
                if domain.confidence >= 90
                else "STABLE"
                if domain.confidence >= 75
                else "WEAK"
            )

            finding_count = len(domain.findings)

            highest_severity = "NONE"

            if finding_count:

                severities = [
                    (
                        finding.severity.value
                        if hasattr(finding.severity, "value")
                        else str(finding.severity)
                    )
                    for finding in domain.findings
                ]

                severity_order = [
                    "CRITICAL",
                    "HIGH",
                    "MEDIUM",
                    "LOW",
                    "INFORMATION",
                ]

                for level in severity_order:
                    if level in severities:
                        highest_severity = level
                        break

            domain_breakdown.append(
                {
                    "name": domain.name,
                    "confidence": round(domain.confidence, 2),
                    "status": status,
                    "finding_count": finding_count,
                    "highest_severity": highest_severity,
                }
            )

            if domain.confidence < 70:

                weak_domains.append(domain.name)

                required_actions.append(
                    f"Review {domain.name} investigation."
                )

        if average_confidence >= 90:

            decision = "ACCEPT"

            residual = (
                InvestigationSeverity.INFORMATION
            )

        elif average_confidence >= 75:

            decision = "CONDITIONAL_ACCEPT"

            residual = (
                InvestigationSeverity.MEDIUM
            )

        else:

            decision = "REJECT"

            residual = (
                InvestigationSeverity.HIGH
            )

        return InvestigationDecision(
            decision=decision,
            confidence=round(
                average_confidence,
                2,
            ),
            rationale=(
                "Allocator decision produced from the "
                "combined institutional investigation "
                "domains."
            ),
            residual_risk=residual,
            required_actions=required_actions,
            metadata={

                "completed_domains": len(
                    completed,
                ),

                "weak_domains": weak_domains,

                "average_confidence": round(
                    average_confidence,
                    2,
                ),

                "evaluation_method":
                    "Institutional Domain Consensus",

                "decision_engine":
                    cls.ENGINE_NAME,

                "domain_breakdown":
                    domain_breakdown,

            },
        )