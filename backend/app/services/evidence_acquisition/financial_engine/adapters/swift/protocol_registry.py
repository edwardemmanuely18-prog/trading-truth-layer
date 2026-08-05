"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Protocol Registry

Canonical registry responsible for storing and
retrieving SWIFT protocol handlers.
"""

from __future__ import annotations

from typing import Dict
from typing import Optional

from .protocol_handler import SwiftProtocolHandler


# ============================================================================
# Registry
# ============================================================================


class SwiftProtocolRegistry:

    def __init__(
        self,
    ) -> None:

        self._handlers: Dict[
            str,
            SwiftProtocolHandler,
        ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        handler: SwiftProtocolHandler,
    ) -> None:

        self._handlers[
            handler.message_type
        ] = handler

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def handler(
        self,
        message_type: str,
    ) -> Optional[
        SwiftProtocolHandler
    ]:

        return self._handlers.get(
            message_type,
        )

    def supports(
        self,
        message_type: str,
    ) -> bool:

        return (
            message_type
            in self._handlers
        )

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def handlers(
        self,
    ) -> list[
        SwiftProtocolHandler
    ]:

        return list(
            self._handlers.values()
        )

    def message_types(
        self,
    ) -> list[str]:

        return sorted(
            self._handlers.keys()
        )


# ============================================================================
# Singleton
# ============================================================================

protocol_registry = (
    SwiftProtocolRegistry()
)


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "SwiftProtocolRegistry",

    "protocol_registry",

]