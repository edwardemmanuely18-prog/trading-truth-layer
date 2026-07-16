from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class BrokerEngine:
    """
    Institutional Broker Investigation Engine.

    Investigates canonical broker payloads produced by the
    BrokerProvider.

    Never queries the database.

    Never modifies broker state.

    Never performs broker synchronization.
    """

    ENGINE_NAME = "Broker"

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

        payload = provider_payloads.get("brokers")

        findings: list[InvestigationFinding] = []

        confidence = 100.0

        metadata: dict[str, Any] = {}

        # ----------------------------------------------------
        # Provider availability
        # ----------------------------------------------------

        if payload is None:

            findings.append(
                InvestigationFinding(
                    id="BROKER-001",
                    title="Broker provider unavailable",
                    description=(
                        "The Broker Provider did not return a "
                        "canonical payload."
                    ),
                    severity=InvestigationSeverity.CRITICAL,
                    confidence=100.0,
                    recommendation=(
                        "Verify BrokerProvider registration "
                        "and execution."
                    ),
                )
            )

            confidence = 0.0

            return InvestigationDomain(
                name="Broker",
                confidence=confidence,
                findings=findings,
                metadata=metadata,
            )

        # ----------------------------------------------------
        # Broker connections
        # ----------------------------------------------------

        connections = payload.get(
            "connections",
            [],
        )

        count = payload.get(
            "count",
            len(connections),
        )

        metadata["broker_count"] = count

        if count == 0:

            findings.append(
                InvestigationFinding(
                    id="BROKER-002",
                    title="No broker connections",
                    description=(
                        "No broker connections were found for "
                        "this workspace."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=100.0,
                    recommendation=(
                        "Connect at least one broker before "
                        "running institutional investigations."
                    ),
                )
            )

            confidence -= 40.0

        else:

            findings.append(
                InvestigationFinding(
                    id="BROKER-000",
                    title="Broker investigation completed",
                    description=(
                        f"{count} broker connection(s) "
                        "available for investigation."
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
            name="Broker",
            confidence=confidence,
            findings=findings,
            metadata=metadata,
        )