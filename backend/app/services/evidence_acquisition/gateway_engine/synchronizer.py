"""
Trading Truth Layer (TTL)

Gateway Engine

Synchronizer

Institutional synchronization pipeline responsible for acquiring,
translating and assembling canonical Gateway evidence.
"""

from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from .models import (
    GatewayEvidencePackage,
    SynchronizationStatistics,
    SynchronizationSummary,
)
from .models import (
    GatewayEvidence,
    SessionEvidence,
    AuthenticationEvidence,
    EndpointEvidence,
    ConnectionEvidence,
    AccountEvidence,
    InstrumentEvidence,
    MarketDataEvidence,
    QuoteEvidence,
    OrderEvidence,
    ExecutionEvidence,
    PositionEvidence,
    TradeEvidence,
)
from .translators import (
    GatewayTranslatorManager,
)
from .normalizer import (
    GatewayNormalizationManager,
)


# ============================================================================
# Synchronization Context
# ============================================================================


class SynchronizationContext:
    """
    Runtime synchronization context.
    """

    def __init__(self) -> None:

        self.started_at = datetime.utcnow()

        self.completed_at: Optional[
            datetime
        ] = None

        self.raw_objects: List[Any] = []

        self.normalized_objects: List[Any] = []

        self.translated_objects: List[Any] = []

        self.statistics = (
            SynchronizationStatistics()
        )

        self.metadata: Dict[str, Any] = {}

    def complete(self) -> None:

        self.completed_at = (
            datetime.utcnow()
        )


# ============================================================================
# Base Synchronizer
# ============================================================================


class BaseGatewaySynchronizer(ABC):
    """
    Base synchronization contract.
    """

    def initialize(self) -> None:

        pass

    def close(self) -> None:

        pass


# ============================================================================
# Gateway Synchronizer
# ============================================================================


class GatewaySynchronizer(
    BaseGatewaySynchronizer
):
    """
    Institutional Gateway synchronization pipeline.
    """

    def __init__(self) -> None:

        self.created_at = datetime.utcnow()


# ============================================================================
# Stage 1
# ============================================================================


    def acquire(
        self,
        *,
        adapter,
        context: SynchronizationContext,
    ) -> Dict[str, Any]:
        """
        Acquire native evidence from the provider.
        """

        acquired = adapter.acquire()

        context.raw_objects.append(
            acquired,
        )

        return acquired


# ============================================================================
# Stage 2
# ============================================================================

    def normalize(
        self,
        *,
        normalization_manager: GatewayNormalizationManager,
        acquired: Dict[str, Any],
        context: SynchronizationContext,
    ) -> Dict[str, Any]:
        """
        Normalize provider-native evidence into canonical dictionaries.
        """

        normalized: Dict[str, Any] = {}

        snapshot = {

            "gateways": acquired.gateways,

            "accounts": acquired.accounts,

            "positions": acquired.positions,

            "orders": acquired.orders,

            "executions": acquired.executions,

            "market_data": acquired.market_data,

        }

        for evidence_type, objects in snapshot.items():

            if objects is None:
                continue

            if not isinstance(objects, list):
                objects = [objects]

            normalized_objects = []

            for obj in objects:

                result = normalization_manager.normalize(
                    evidence_type=evidence_type,
                    obj=obj,
                )

                if not result.successful:
                    continue

                normalized_objects.append(result)

                context.normalized_objects.append(result)

            normalized[evidence_type] = normalized_objects

        return normalized


    def _evidence_class(
        self,
        evidence_type: str,
    ):
        """
        Resolve a synchronization category into its canonical
        Evidence class.
        """

        mapping = {

            "gateways": GatewayEvidence,

            "sessions": SessionEvidence,

            "authentications": AuthenticationEvidence,

            "endpoints": EndpointEvidence,

            "connections": ConnectionEvidence,

            "accounts": AccountEvidence,

            "instruments": InstrumentEvidence,

            "market_data": MarketDataEvidence,

            "quotes": QuoteEvidence,

            "orders": OrderEvidence,

            "executions": ExecutionEvidence,

            "positions": PositionEvidence,

            "trades": TradeEvidence,
        }

        return mapping[evidence_type]

# ============================================================================
# Stage 2
# ============================================================================

    def translate(
        self,
        *,
        translator_manager: GatewayTranslatorManager,
        normalized: Dict[str, Any],
        context: SynchronizationContext,
    ) -> Dict[str, Any]:
        """
        Translate provider-normalized evidence into canonical
        Gateway evidence models.
        """

        translated: Dict[str, Any] = {}

        for evidence_type, objects in normalized.items():

            if objects is None:
                continue

            if not isinstance(objects, list):
                objects = [objects]

            translated_objects = []

            for obj in objects:

                canonical = translator_manager.translate(
                    evidence_type=self._evidence_class(
                        evidence_type,
                    ),
                    native_object=obj,
                )

                translated_objects.append(canonical)

                context.translated_objects.append(canonical)

            translated[evidence_type] = translated_objects

        return translated


# ============================================================================
# Stage 3
# ============================================================================

    def assemble(
        self,
        *,
        translated: Dict[str, Any],
        context: SynchronizationContext,
    ) -> GatewayEvidencePackage:
        """
        Assemble the canonical GatewayEvidencePackage.
        """

        summary = SynchronizationSummary(
            started_at=context.started_at,
            completed_at=datetime.utcnow(),
            statistics=context.statistics,
        )

        package = GatewayEvidencePackage(

            summary=summary,

            gateway=(
                translated.get("gateways", [None])[0]
                if translated.get("gateways")
                else None
            ),

            session=(
                translated.get("sessions", [None])[0]
                if translated.get("sessions")
                else None
            ),

            authentication=(
                translated.get("authentications", [None])[0]
                if translated.get("authentications")
                else None
            ),

            endpoint=(
                translated.get("endpoints", [None])[0]
                if translated.get("endpoints")
                else None
            ),

            connection=(
                translated.get("connections", [None])[0]
                if translated.get("connections")
                else None
            ),

            account=(
                translated.get("accounts", [None])[0]
                if translated.get("accounts")
                else None
            ),

            instruments=translated.get(
                "instruments",
                [],
            ),

            market_data=translated.get(
                "market_data",
                [],
            ),

            quotes=translated.get(
                "quotes",
                [],
            ),

            orders=translated.get(
                "orders",
                [],
            ),

            executions=translated.get(
                "executions",
                [],
            ),

            positions=translated.get(
                "positions",
                [],
            ),

            trades=translated.get(
                "trades",
                [],
            ),
        )

        context.complete()

        return package


# ============================================================================
# Synchronization Pipeline
# ============================================================================

    def synchronize(
        self,
        *,
        adapter,
        normalization_manager: GatewayNormalizationManager,
        translator_manager: GatewayTranslatorManager,
    ) -> GatewayEvidencePackage:
        """
        Execute the complete synchronization pipeline.

            Acquire
                ↓
            Normalize
                ↓
            Translate
                ↓
            Assemble
                ↓
        GatewayEvidencePackage
        """

        context = SynchronizationContext()

        acquired = self.acquire(
            adapter=adapter,
            context=context,
        )

        context.statistics.evidence_objects = (

            len(acquired.gateways)

            + len(acquired.accounts)

            + len(acquired.positions)

            + len(acquired.orders)

            + len(acquired.executions)

            + len(acquired.market_data)

        )

        normalized = self.normalize(
            normalization_manager=normalization_manager,
            acquired=acquired,
            context=context,
        )

        context.statistics.infrastructure_objects = len(
            context.normalized_objects,
        )

        translated = self.translate(
            translator_manager=translator_manager,
            normalized=normalized,
            context=context,
        )

        context.statistics.translated_objects = len(
            context.translated_objects,
        )

        return self.assemble(
            translated=translated,
            context=context,
        )


# ============================================================================
# Runtime Statistics
# ============================================================================


    @property
    def uptime(self):
        """
        Synchronizer uptime.
        """

        return datetime.utcnow() - self.created_at


    def statistics(self) -> dict:
        """
        Runtime synchronizer statistics.
        """

        return {

            "created_at": self.created_at,

            "uptime_seconds": self.uptime.total_seconds(),
        }


# ============================================================================
# Health
# ============================================================================


    def health(self) -> dict:
        """
        Synchronizer health.
        """

        return {

            "status": "healthy",

            "created_at": self.created_at,

            "uptime_seconds": self.uptime.total_seconds(),
        }


# ============================================================================
# Diagnostics
# ============================================================================


    def diagnostics(self) -> dict:
        """
        Complete synchronizer diagnostics.
        """

        return {

            "class": self.__class__.__name__,

            "statistics": self.statistics(),

            "health": self.health(),
        }


# ============================================================================
# Representation
# ============================================================================


    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"created_at={self.created_at.isoformat()})"

        )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "SynchronizationContext",

    "BaseGatewaySynchronizer",

    "GatewaySynchronizer",
]