from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class BehaviorEngine:
    """
    Institutional Behavior Investigation Engine.

    This engine correlates institutional activity across
    canonical provider payloads.

    It NEVER:

    - queries the database
    - mutates data
    - recalculates verification
    - performs synchronization

    It investigates behavioural indicators using existing
    canonical provider outputs.
    """

    ENGINE_NAME = "Behavior"

    @classmethod
    def build(
        cls,
        *,
        context: Any,
    ) -> InvestigationDomain:

        provider_payloads = getattr(
            context,
            "provider_payloads",
            {},
        )

        audit = provider_payloads.get("audit")

        reviews = provider_payloads.get("reviews")

        brokers = provider_payloads.get("brokers")

        sync = provider_payloads.get("sync")

        execution = provider_payloads.get("execution")

        verification = provider_payloads.get("verification")

        findings: list[InvestigationFinding] = []

        confidence = 100.0

        metadata: dict[str, Any] = {}

        audit_count = len(audit) if audit else 0
        review_count = len(reviews) if reviews else 0

        broker_count = 0
        if brokers:
            broker_count = brokers.get("count", 0)

        sync_jobs = 0
        if sync:
            sync_jobs = len(sync.get("jobs", []))

        metadata.update(
            {
                "audit_events": audit_count,
                "reviews": review_count,
                "brokers": broker_count,
                "sync_jobs": sync_jobs,
                "execution_available": execution is not None,
                "verification_available": verification is not None,
            }
        )

        # ----------------------------------------------------
        # Behaviour completeness
        # ----------------------------------------------------

        if audit_count == 0:

            findings.append(
                InvestigationFinding(
                    id="BEHAVIOR-001",
                    title="No audit history",
                    description=(
                        "Behaviour analysis has limited evidence "
                        "because no audit history exists."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=100.0,
                    recommendation=(
                        "Enable institutional audit logging."
                    ),
                )
            )

            confidence -= 10.0

        if review_count == 0:

            findings.append(
                InvestigationFinding(
                    id="BEHAVIOR-002",
                    title="No review activity",
                    description=(
                        "No review statements were available "
                        "for behavioural investigation."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=100.0,
                    recommendation=(
                        "Complete institutional reviews."
                    ),
                )
            )

            confidence -= 10.0

        if broker_count == 0:

            findings.append(
                InvestigationFinding(
                    id="BEHAVIOR-003",
                    title="No broker activity",
                    description=(
                        "No broker connections were available "
                        "for behavioural investigation."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=100.0,
                    recommendation=(
                        "Connect at least one broker."
                    ),
                )
            )

            confidence -= 15.0

        if sync_jobs == 0:

            findings.append(
                InvestigationFinding(
                    id="BEHAVIOR-004",
                    title="No synchronization history",
                    description=(
                        "Behaviour cannot be reconstructed "
                        "without synchronization history."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=100.0,
                    recommendation=(
                        "Run broker synchronization."
                    ),
                )
            )

            confidence -= 10.0

        if execution is None:

            findings.append(
                InvestigationFinding(
                    id="BEHAVIOR-005",
                    title="Execution investigation unavailable",
                    description=(
                        "Execution investigation results were "
                        "not available."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=100.0,
                    recommendation=(
                        "Complete execution investigation."
                    ),
                )
            )

            confidence -= 15.0

        if verification is None:

            findings.append(
                InvestigationFinding(
                    id="BEHAVIOR-006",
                    title="Verification unavailable",
                    description=(
                        "Behaviour investigation could not "
                        "correlate verification outputs."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=100.0,
                    recommendation=(
                        "Complete verification investigation."
                    ),
                )
            )

            confidence -= 15.0

        if not findings:

            findings.append(
                InvestigationFinding(
                    id="BEHAVIOR-000",
                    title="Behaviour investigation completed",
                    description=(
                        "Cross-domain institutional behaviour "
                        "appears internally consistent."
                    ),
                    severity=InvestigationSeverity.INFORMATION,
                    confidence=100.0,
                    recommendation="No action required.",
                )
            )

        confidence = max(
            0.0,
            min(
                confidence,
                100.0,
            ),
        )

        return InvestigationDomain(
            name="Behavior",
            confidence=confidence,
            findings=findings,
            metadata=metadata,
        )