"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Protocol Handler

Canonical interface implemented by every SWIFT protocol
handler (MT103, MT202, MT700, ...).

The SwiftAdapter never performs protocol-specific
processing directly. It delegates processing to a
registered protocol handler.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from typing import Any


# ============================================================================
# Protocol Handler
# ============================================================================


class SwiftProtocolHandler(ABC):
    """
    Base class implemented by every SWIFT protocol handler.
    """

    @property
    @abstractmethod
    def message_type(
        self,
    ) -> str:
        """
        Canonical SWIFT message type.

        Example:

            MT103
            MT202
            MT700
        """

    @abstractmethod
    def process(
        self,
        adapter: Any,
        message,
        fields,
    ) -> dict:
        """
        Process a parsed FIN message and return the
        canonical Financial Engine payload.
        """


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "SwiftProtocolHandler",
]