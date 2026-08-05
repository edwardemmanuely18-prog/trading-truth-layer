"""
Trading Truth Layer (TTL)

Evidence Acquisition

Acquisition Bridge

Institutional bridge between the Evidence Acquisition subsystem and the
Universal Evidence Adapter (UEA).

Responsibilities
----------------
• Register acquisition engines
• Provide a unified acquisition entry point
• Expose engine health
• Expose engine statistics

This bridge intentionally DOES NOT:

• translate evidence
• validate evidence
• deduplicate evidence
• publish evidence
• verify evidence

Those responsibilities belong to the Universal Evidence Adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional

from .base_engine import AcquisitionEngine

from .desktop_trading_engine.engine import DesktopTradingEngine
from .financial_engine.engine import FinancialEngine
from .gateway_engine.engine import GatewayEngine


# ============================================================================
# Engine Types
# ============================================================================


class AcquisitionEngineType(str, Enum):
    """
    Supported acquisition engines.
    """

    DESKTOP = "desktop"

    FINANCIAL = "financial"

    GATEWAY = "gateway"


# ============================================================================
# Acquisition Result
# ============================================================================


@dataclass(slots=True)
class AcquisitionResult:
    """
    Result returned by the Acquisition Bridge.
    """

    engine: AcquisitionEngineType

    successful: bool

    started_at: datetime = field(
        default_factory=datetime.utcnow
    )

    completed_at: Optional[datetime] = None

    duration_ms: float = 0.0

    payload: Any = None

    error: Optional[Exception] = None


# ============================================================================
# Bridge Statistics
# ============================================================================


@dataclass(slots=True)
class BridgeStatistics:
    """
    Runtime bridge statistics.
    """

    registered_engines: int = 0

    desktop_registered: bool = False

    financial_registered: bool = False

    gateway_registered: bool = False


# ============================================================================
# Bridge Health
# ============================================================================


@dataclass(slots=True)
class BridgeHealth:
    """
    Overall bridge health.
    """

    healthy: bool

    desktop: bool

    financial: bool

    gateway: bool


# ============================================================================
# Acquisition Bridge
# ============================================================================


class AcquisitionBridge:
    """
    Institutional acquisition bridge.

    Serves as the single entry point between Evidence Acquisition
    and the Universal Evidence Adapter.
    """

    def __init__(self) -> None:

        self._engines: Dict[
            AcquisitionEngineType,
            AcquisitionEngine,
        ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_engine(
        self,
        engine_type: AcquisitionEngineType,
        engine: AcquisitionEngine,
    ) -> None:
        """
        Register an acquisition engine.
        """

        self._engines[engine_type] = engine

    def register_desktop_engine(
        self,
        engine: DesktopTradingEngine,
    ) -> None:

        self.register_engine(
            AcquisitionEngineType.DESKTOP,
            engine,
        )

    def register_financial_engine(
        self,
        engine: FinancialEngine,
    ) -> None:

        self.register_engine(
            AcquisitionEngineType.FINANCIAL,
            engine,
        )

    def register_gateway_engine(
        self,
        engine: GatewayEngine,
    ) -> None:

        self.register_engine(
            AcquisitionEngineType.GATEWAY,
            engine,
        )

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def has_engine(
        self,
        engine_type: AcquisitionEngineType,
    ) -> bool:

        return engine_type in self._engines

    def engine(
        self,
        engine_type: AcquisitionEngineType,
    ) -> AcquisitionEngine:

        return self._engines[engine_type]

    @property
    def desktop_engine(
        self,
    ) -> DesktopTradingEngine | None:

        return self._engines.get(
            AcquisitionEngineType.DESKTOP
        )

    @property
    def financial_engine(
        self,
    ) -> FinancialEngine | None:

        return self._engines.get(
            AcquisitionEngineType.FINANCIAL
        )

    @property
    def gateway_engine(
        self,
    ) -> GatewayEngine | None:

        return self._engines.get(
            AcquisitionEngineType.GATEWAY
        )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(
        self,
    ) -> BridgeStatistics:
        """
        Bridge statistics.
        """

        return BridgeStatistics(

            registered_engines=len(
                self._engines
            ),

            desktop_registered=self.desktop_engine
            is not None,

            financial_registered=self.financial_engine
            is not None,

            gateway_registered=self.gateway_engine
            is not None,
        )

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(
        self,
    ) -> BridgeHealth:
        """
        Aggregate bridge health.
        """

        def _healthy(
            engine: AcquisitionEngine | None,
        ) -> bool:

            if engine is None:
                return False

            try:
                return bool(
                    engine.health().get(
                        "healthy",
                        False,
                    )
                )

            except Exception:
                return False

        desktop_ok = _healthy(
            self.desktop_engine
        )

        financial_ok = _healthy(
            self.financial_engine
        )

        gateway_ok = _healthy(
            self.gateway_engine
        )

        return BridgeHealth(

            healthy=(

                desktop_ok

                and financial_ok

                and gateway_ok
            ),

            desktop=desktop_ok,

            financial=financial_ok,

            gateway=gateway_ok,
        )

        # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        engine_type: AcquisitionEngineType,
        *args,
        **kwargs,
    ) -> AcquisitionResult:
        """
        Execute evidence acquisition through a registered engine.

        The bridge intentionally delegates acquisition to the engine.

        Translation into TTL canonical evidence remains the
        responsibility of the Universal Evidence Adapter.
        """

        engine = self._engines.get(engine_type)

        if engine is None:

            return AcquisitionResult(

                engine=engine_type,

                successful=False,

                error=RuntimeError(
                    f"No engine registered for "
                    f"{engine_type.value}."
                ),
            )

        try:

            payload = engine.acquire(
                *args,
                **kwargs,
            )

            return AcquisitionResult(

                engine=engine_type,

                successful=True,

                payload=payload,
            )

        except Exception as exc:

            return AcquisitionResult(

                engine=engine_type,

                successful=False,

                error=exc,
            )

    # ------------------------------------------------------------------

    def acquire_all(
        self,
        requests: dict[
            AcquisitionEngineType,
            dict,
        ],
    ) -> list[AcquisitionResult]:
        """
        Execute acquisition across multiple engines.

        Parameters
        ----------
        requests

            Mapping of engine type to keyword arguments.

        Example
        -------
        {
            AcquisitionEngineType.DESKTOP: {
                "connector": mt5_connector,
            },

            AcquisitionEngineType.FINANCIAL: {
                "provider": swift_provider,
            },
        }
        """

        results: list[
            AcquisitionResult
        ] = []

        for engine_type, kwargs in requests.items():

            results.append(

                self.acquire(

                    engine_type,

                    **kwargs,
                )
            )

        return results


# ============================================================================
# Global Bridge
# ============================================================================


acquisition_bridge = AcquisitionBridge()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "AcquisitionEngineType",

    "AcquisitionResult",

    "BridgeStatistics",

    "BridgeHealth",

    "AcquisitionBridge",

    "acquisition_bridge",
]