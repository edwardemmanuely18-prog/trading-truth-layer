"""
Trading Truth Layer (TTL)

Evidence Acquisition

Bootstrap

Canonical composition root for the
Evidence Acquisition subsystem.

Responsibilities
----------------
• Construct the application service
• Wire the runtime
• Wire the acquisition bridge
• Register acquisition engines
• Initialize subsystem lifecycle

This module intentionally contains
no business logic.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict

from .runtime import EvidenceAcquisitionRuntime

from .acquisition_bridge import (
    AcquisitionBridge,
    AcquisitionEngineType,
)
from .base_engine import AcquisitionEngine
from .desktop_trading_engine.engine import (
    desktop_trading_engine,
)
from .service import EvidenceAcquisitionService


# ============================================================================
# Bootstrap State
# ============================================================================


class BootstrapState(str, Enum):

    CREATED = "created"

    INITIALIZED = "initialized"

    RUNNING = "running"

    STOPPED = "stopped"


# ============================================================================
# Bootstrap
# ============================================================================


class EvidenceAcquisitionBootstrap:
    """
    Canonical composition root for the
    Evidence Acquisition subsystem.
    """

    def __init__(self) -> None:

        #
        # Bootstrap State
        #

        self.state = BootstrapState.CREATED

        #
        # Core Runtime
        #

        self.runtime = EvidenceAcquisitionRuntime()

        #
        # Acquisition Bridge
        #

        self.bridge = AcquisitionBridge()

        #
        # Application Service
        #

        self.service = EvidenceAcquisitionService(

            runtime=self.runtime,

            bridge=self.bridge,

        )

        #
        # Register every production-ready acquisition engine.
        #

        self._register_default_engines()

        #
        # Complete subsystem bootstrap.
        #

        self._bootstrap_subsystem()

    # ------------------------------------------------------------------
    # Engine Registration
    # ------------------------------------------------------------------

    def register_engine(
        self,
        name: str,
        engine_type: AcquisitionEngineType,
        engine: AcquisitionEngine,
    ) -> None:
        """
        Register an acquisition engine with both
        the Runtime and the Acquisition Bridge.
        """

        #
        # Runtime
        #

        self.runtime.register_engine(
            name,
            engine,
        )

        #
        # Bridge
        #

        self.bridge.register_engine(
            engine_type,
            engine,
        )

    @property
    def engines(
        self,
    ) -> Dict[str, AcquisitionEngine]:
        """
        Registered acquisition engines.
        """

        return self.runtime.engines

    # ------------------------------------------------------------------
    # Default Engine Registration
    # ------------------------------------------------------------------

    def _register_default_engines(
        self,
    ) -> None:
        """
        Register every production-ready acquisition engine.

        Only engines that actively participate in the current
        Evidence Acquisition workflow are registered here.

        Additional engines (Gateway, Financial, etc.) will be
        registered once their integration into the runtime is
        complete.
        """

        self.register_engine(

            name=desktop_trading_engine.name,

            engine_type=AcquisitionEngineType.DESKTOP,

            engine=desktop_trading_engine,

        )

        #
        # Future registrations
        #
        # Gateway Engine
        # Financial Engine
        #
        # These engines will be registered once their runtime
        # integration is complete.

    # ------------------------------------------------------------------
    # Bootstrap Lifecycle
    # ------------------------------------------------------------------

    def _bootstrap_subsystem(
        self,
    ) -> None:
        """
        Complete canonical subsystem bootstrap.

        This method executes the complete institutional startup
        sequence exactly once.

            Register Engines
                    ↓
            Initialize Runtime
                    ↓
            Start Runtime
        """

        #
        # Runtime
        #

        self.initialize()

        self.start()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Initialize the subsystem runtime.
        """

        if self.state != BootstrapState.CREATED:
            return

        self.runtime.initialize()

        self.state = BootstrapState.INITIALIZED

    def start(self) -> None:
        """
        Start the subsystem runtime.
        """

        if self.state == BootstrapState.RUNNING:
            return

        if self.state == BootstrapState.CREATED:
            self.initialize()

        self.runtime.start()

        self.state = BootstrapState.RUNNING

    def restart(self) -> None:
        """
        Restart the subsystem runtime.
        """

        self.runtime.restart()

        self.state = BootstrapState.RUNNING


# ============================================================================
# Canonical Bootstrap
# ============================================================================


bootstrap = EvidenceAcquisitionBootstrap()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "BootstrapState",

    "EvidenceAcquisitionBootstrap",

    "bootstrap",

]