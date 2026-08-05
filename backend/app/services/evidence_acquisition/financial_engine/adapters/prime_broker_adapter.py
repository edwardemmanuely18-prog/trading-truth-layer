"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Institutional Prime Broker Adapter

Canonical prime broker acquisition adapter.

The Prime Broker Adapter provides the Financial Engine entry
point for prime brokerage evidence acquisition.

Provider-specific processing is delegated to registered
prime broker adapters.

The adapter itself contains no provider-specific parsing
or business transformation logic.
"""

from __future__ import annotations

from typing import Any

from .base_adapter import FinancialAdapter


# ============================================================================
# Prime Broker Adapter
# ============================================================================


class PrimeBrokerAdapter(FinancialAdapter):
    """
    Canonical prime broker acquisition adapter.

    Current Providers
    -----------------

    (Registered dynamically)

    Future
    ------

    • Interactive Brokers Prime

    • Goldman Sachs Prime

    • Morgan Stanley Prime

    • JP Morgan Prime

    • UBS Prime

    • Fidelity Prime

    • StoneX Prime

    • Prime FIX

    • Prime REST APIs
    """

    PROVIDER = "PRIME_BROKER"

    DESCRIPTION = (
        "Institutional Prime Broker Adapter"
    )

    def __init__(
        self,
        connector,
    ) -> None:

        super().__init__(
            connector,
        )

        self._providers: dict[
            str,
            FinancialAdapter,
        ] = {}

    # ------------------------------------------------------------------
    # Adapter Metadata
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> str:

        return self.PROVIDER

    @property
    def description(
        self,
    ) -> str:

        return self.DESCRIPTION

    # ------------------------------------------------------------------
    # Provider Registration
    # ------------------------------------------------------------------

    def register_provider(
        self,
        provider_name: str,
        adapter: FinancialAdapter,
    ) -> None:
        """
        Register a provider-specific prime broker adapter.
        """

        self._providers[
            provider_name
        ] = adapter

    # ------------------------------------------------------------------
    # Provider Discovery
    # ------------------------------------------------------------------

    def supported_providers(
        self,
    ) -> list[str]:

        return sorted(

            self._providers.keys()

        )

    def supports(
        self,
        provider_name: str,
    ) -> bool:

        return (
            provider_name
            in self._providers
        )

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        *,
        provider_name: str,
        payload: Any,
    ) -> list[Any]:
        """
        Acquire canonical prime broker evidence.
        """

        adapter = self._providers.get(
            provider_name,
        )

        if adapter is None:

            raise ValueError(

                f"Unsupported prime broker provider: {provider_name}"

            )

        return adapter.acquire(

            payload=payload,

        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "PrimeBrokerAdapter",
]