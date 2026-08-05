"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Institutional Payment Adapter

Canonical payment acquisition adapter.

The Payment Adapter provides the Financial Engine entry point for
payment evidence acquisition.

Protocol-specific processing is delegated to the canonical
SWIFT Adapter.

The adapter itself contains no protocol parsing logic.
"""

from __future__ import annotations

from typing import Any

from .base_adapter import FinancialAdapter

from .swift.swift_adapter import SwiftAdapter


# ============================================================================
# Payment Adapter
# ============================================================================


class PaymentAdapter(FinancialAdapter):
    """
    Canonical payment acquisition adapter.

    Supported Providers
    -------------------

    • SWIFT
        • MT103
        • MT202

    Future
    ------

    • ISO20022 (pacs.*)
    • Fedwire
    • CHIPS
    • SEPA
    • RTP
    • Bank APIs
    """

    PROVIDER = "PAYMENT"

    DESCRIPTION = (
        "Institutional Payment Adapter"
    )

    def __init__(
        self,
        connector,
    ) -> None:

        super().__init__(
            connector,
        )

        self._swift = SwiftAdapter(
            connector,
        )

    # ------------------------------------------------------------------
    # Provider Metadata
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
    # Supported Protocols
    # ------------------------------------------------------------------

    def supported_message_types(
        self,
    ) -> list[str]:

        return sorted(

            self._swift.supported_message_types()

        )

    def supports(
        self,
        message_type: str,
    ) -> bool:

        return self._swift.supports(
            message_type,
        )

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        *,
        message_type: str,
        raw_message: str,
    ) -> list[Any]:
        """
        Acquire canonical payment evidence.

        Processing is delegated to the canonical
        SWIFT Adapter.
        """

        return self._swift.acquire(

            message_type=message_type,

            raw_message=raw_message,

        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "PaymentAdapter",
]