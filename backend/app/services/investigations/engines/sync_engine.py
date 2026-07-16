from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class SyncEngine:
    """
    Institutional Synchronization Investigation Engine.

    Investigates the canonical synchronization payload
    produced by SyncJobProvider.

    This engine NEVER:

    - queries the database
    - performs synchronization
    - modifies synchronization jobs

    It only investigates operational synchronization
    health.
    """

    ENGINE_NAME = "Synchronization"

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

        payload = provider_payloads.get("sync")

        findings: list[InvestigationFinding] = []

        confidence = 100.0

        metadata: dict[str, Any] = {}

        # ----------------------------------------------------
        # Provider availability
        # ----------------------------------------------------

        if payload is None:

            findings.append(
                InvestigationFinding(
                    id="SYNC-001",
                    title="Synchronization provider unavailable",
                    description=(
                        "The SyncJobProvider did not return a "
                        "canonical payload."
                    ),
                    severity=InvestigationSeverity.CRITICAL,
                    confidence=100.0,
                    recommendation=(
                        "Verify SyncJobProvider registration "
                        "and execution."
                    ),
                )
            )

            return InvestigationDomain(
                name="Synchronization",
                confidence=0.0,
                findings=findings,
                metadata=metadata,
            )

        jobs = payload.get(
            "jobs",
            [],
        )

        broker_connections = payload.get(
            "broker_connections",
            [],
        )

        trades = payload.get(
            "trades",
            [],
        )

        metadata.update(
            {
                "sync_jobs": len(jobs),
                "broker_connections": len(broker_connections),
                "trade_count": len(trades),
            }
        )

        # ----------------------------------------------------
        # Operational checks
        # ----------------------------------------------------

        if len(broker_connections) == 0:

            findings.append(
                InvestigationFinding(
                    id="SYNC-002",
                    title="No broker connections",
                    description=(
                        "Synchronization cannot occur because "
                        "no broker connections exist."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=100.0,
                    recommendation=(
                        "Create at least one broker connection."
                    ),
                )
            )

            confidence -= 30.0

        if len(jobs) == 0:

            findings.append(
                InvestigationFinding(
                    id="SYNC-003",
                    title="No synchronization jobs",
                    description=(
                        "No synchronization history is "
                        "available."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=100.0,
                    recommendation=(
                        "Execute broker synchronization."
                    ),
                )
            )

            confidence -= 20.0

        if len(trades) == 0:

            findings.append(
                InvestigationFinding(
                    id="SYNC-004",
                    title="No synchronized trades",
                    description=(
                        "Synchronization completed without "
                        "producing any trade history."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=100.0,
                    recommendation=(
                        "Verify broker imports and "
                        "synchronization jobs."
                    ),
                )
            )

            confidence -= 20.0

        if not findings:

            findings.append(
                InvestigationFinding(
                    id="SYNC-000",
                    title="Synchronization investigation passed",
                    description=(
                        "Synchronization infrastructure appears "
                        "healthy."
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
            name="Synchronization",
            confidence=confidence,
            findings=findings,
            metadata=metadata,
        )