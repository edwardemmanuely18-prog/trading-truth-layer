"""
SWIFT simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class SwiftSimulator(BaseProviderSimulator):
    """
    SWIFT network simulator.
    """

    @property
    def provider_name(self) -> str:
        return "swift"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "bic",
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "SWIFT simulator is not connected."
            )

        return [
            {
                "network": "SWIFT",
                "bic": "TTLBUS33",
                "message_type": "MT103",
                "reference": "SWIFT-100001",
            }
        ]


__all__ = [
    "SwiftSimulator",
]