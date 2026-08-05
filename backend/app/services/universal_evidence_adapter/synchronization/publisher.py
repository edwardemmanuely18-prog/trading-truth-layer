from __future__ import annotations

"""
Institutional Evidence Publisher

The Evidence Publisher is responsible for distributing canonical evidence
to registered TTL consumers.

Responsibilities
----------------
- Register subscribers
- Publish canonical evidence
- Broadcast synchronization events
- Collect publishing metrics
- Isolate downstream failures

The publisher does NOT:
- Verify evidence
- Canonicalize evidence
- Modify evidence
- Deduplicate evidence
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


# ============================================================================
# Consumer Interface
# ============================================================================

class EvidenceConsumer(Protocol):
    """
    Interface implemented by every evidence consumer.
    """

    def consume(self, evidence: Any) -> None:
        ...


# ============================================================================
# Publish Result
# ============================================================================

@dataclass(slots=True)
class PublishResult:

    consumer: str

    success: bool

    timestamp: datetime

    error: str | None = None


# ============================================================================
# Publisher Metrics
# ============================================================================

@dataclass(slots=True)
class PublisherMetrics:

    published: int = 0

    successful_deliveries: int = 0

    failed_deliveries: int = 0

    registered_consumers: int = 0


# ============================================================================
# Evidence Publisher
# ============================================================================

class EvidencePublisher:
    """
    Institutional evidence publisher.
    """

    def __init__(self) -> None:

        self._consumers: dict[str, EvidenceConsumer] = {}

        self._metrics = PublisherMetrics()

    # ----------------------------------------------------------------------

    @property
    def metrics(self) -> PublisherMetrics:
        return self._metrics

    # ----------------------------------------------------------------------

    def register(
        self,
        name: str,
        consumer: EvidenceConsumer,
    ) -> None:
        """
        Register a downstream consumer.
        """

        self._consumers[name] = consumer

        self._metrics.registered_consumers = len(self._consumers)

    # ----------------------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> bool:
        """
        Remove a consumer.
        """

        if name not in self._consumers:
            return False

        del self._consumers[name]

        self._metrics.registered_consumers = len(self._consumers)

        return True

    # ----------------------------------------------------------------------

    def publish(
        self,
        evidence: Any,
    ) -> list[PublishResult]:
        """
        Publish canonical evidence to all registered consumers.
        """

        results: list[PublishResult] = []

        self._metrics.published += 1

        for name, consumer in self._consumers.items():

            try:

                consumer.consume(evidence)

                self._metrics.successful_deliveries += 1

                results.append(
                    PublishResult(
                        consumer=name,
                        success=True,
                        timestamp=datetime.now(timezone.utc),
                    )
                )

            except Exception as exc:

                self._metrics.failed_deliveries += 1

                results.append(
                    PublishResult(
                        consumer=name,
                        success=False,
                        timestamp=datetime.now(timezone.utc),
                        error=str(exc),
                    )
                )

        return results

    # ----------------------------------------------------------------------

    def consumers(self) -> list[str]:
        """
        Return registered consumer names.
        """

        return sorted(self._consumers.keys())

    # ----------------------------------------------------------------------

    def statistics(self) -> dict[str, Any]:
        """
        Export publisher metrics.
        """

        return {
            "published": self._metrics.published,
            "registered_consumers": self._metrics.registered_consumers,
            "successful_deliveries": self._metrics.successful_deliveries,
            "failed_deliveries": self._metrics.failed_deliveries,
        }

    # ----------------------------------------------------------------------

    def validate(self) -> list[str]:
        """
        Validate publisher state.
        """

        issues: list[str] = []

        if self._metrics.registered_consumers != len(self._consumers):
            issues.append(
                "Registered consumer metric does not match actual consumers."
            )

        if self._metrics.successful_deliveries < 0:
            issues.append(
                "Successful deliveries cannot be negative."
            )

        if self._metrics.failed_deliveries < 0:
            issues.append(
                "Failed deliveries cannot be negative."
            )

        return issues

    # ----------------------------------------------------------------------

    def process(
        self,
        evidence: CanonicalEvidence,
    ) -> list[PublishResult]:
        """
        Pipeline entry point.

        Publish canonical evidence to all
        registered consumers.
        """

        return self.publish(evidence)