"""
MT799 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT799Simulator(BaseProviderSimulator):
    """
    MT799 free-format message simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt799"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "bic",
            "session",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "MT799 simulator is not connected."
            )

        return [
            {
                "message_type": "MT799",
                "reference": "MSG-799001",
                "subject": "Proof of Funds",
                "status": "DELIVERED",
            }
        ]


__all__ = [
    "MT799Simulator",
]