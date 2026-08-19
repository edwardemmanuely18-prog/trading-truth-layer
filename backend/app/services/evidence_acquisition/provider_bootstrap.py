"""
Trading Truth Layer (TTL)

Evidence Acquisition

Provider Bootstrap

Canonical provider discovery bridge for the
Evidence Acquisition Runtime.

Responsibilities
----------------
• Discover providers exposed by registered acquisition engines
• Register discovered providers into Runtime

This module intentionally DOES NOT:

• connect to providers
• authenticate providers
• synchronize providers
• acquire evidence
"""

from __future__ import annotations

from .runtime import EvidenceAcquisitionRuntime


# ============================================================================
# Provider Bootstrap
# ============================================================================

class ProviderBootstrap:
    """
    Canonical Provider Bootstrap.

    Provider discovery is delegated to the registered acquisition engines.
    This class does not instantiate provider registries directly and does
    not create provider connections.
    """

    def __init__(
        self,
        runtime: EvidenceAcquisitionRuntime,
    ) -> None:

        self.runtime = runtime

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_all(self) -> None:
        """
        Register providers exposed by every currently registered
        acquisition engine.

        The Runtime remains the canonical provider registry.
        """

        for engine in self.runtime.engines.values():

            providers = getattr(
                engine,
                "providers",
                (),
            )

            for provider in providers:

                self.runtime.register_provider(
                    name=provider.name,
                    engine=engine.name,
                    provider=provider,
                )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "ProviderBootstrap",
]