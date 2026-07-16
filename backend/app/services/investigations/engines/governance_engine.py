from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class GovernanceEngine:
    """
    Institutional Governance Investigation Engine.

    Investigates governance quality using canonical
    provider payloads.

    This engine NEVER:

    - queries the database
    - mutates audit history
    - recalculates permissions

    It only evaluates governance evidence.
    """

    ENGINE_NAME = "Governance"

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

        default_impact = {

            "claims": len(
                provider_payloads.get(
                    "claims",
                    [],
                ),
            ),

            "trades": len(
                provider_payloads
                .get(
                    "sync",
                    {},
                )
                .get(
                    "trades",
                    [],
                ),
            ),

            "members": len(
                provider_payloads.get(
                    "members",
                    [],
                ),
            ),

            "accounts": len(
                provider_payloads.get(
                    "brokers",
                    [],
                ),
            ),

            "sync_jobs": len(
                provider_payloads
                .get(
                    "sync",
                    {},
                )
                .get(
                    "jobs",
                    [],
                ),
            ),

        }

        audit_events = provider_payloads.get("audit")

        findings: list[InvestigationFinding] = []

        confidence = 100.0

        metadata: dict[str, Any] = {}

        # ----------------------------------------------------
        # Provider availability
        # ----------------------------------------------------

        if audit_events is None:

            findings.append(
                InvestigationFinding(
                    id="GOV-001",
                    title="Audit provider unavailable",
                    description=(
                        "The AuditProvider did not return a "
                        "canonical payload."
                    ),
                    severity=InvestigationSeverity.CRITICAL,
                    confidence=100.0,
                    recommendation=(
                        "Verify AuditProvider registration "
                        "and execution."
                    ),

                    impact=default_impact.copy(),
                )
            )

            return InvestigationDomain(
                name="Governance",
                confidence=0.0,
                findings=findings,
                metadata=metadata,
            )

        audit_count = len(audit_events)

        metadata["audit_event_count"] = audit_count

        # ----------------------------------------------------
        # Governance coverage
        # ----------------------------------------------------

        if audit_count == 0:

            findings.append(
                InvestigationFinding(
                    id="GOV-002",
                    title="No audit history",
                    description=(
                        "No institutional audit events are "
                        "available for investigation."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=100.0,
                    recommendation=(
                        "Enable audit collection before relying "
                        "on governance assessments."
                    ),

                    impact=default_impact.copy(),
                )
            )

            confidence -= 35.0

        else:

            findings.append(
                InvestigationFinding(
                    id="GOV-000",
                    title="Governance investigation completed",
                    description=(
                        f"{audit_count} audit event(s) "
                        "available for governance analysis."
                    ),
                    severity=InvestigationSeverity.INFORMATION,
                    confidence=100.0,
                    recommendation="No action required.",

                    impact=default_impact.copy(),
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
            name="Governance",
            confidence=confidence,
            findings=findings,
            metadata=metadata,
        )