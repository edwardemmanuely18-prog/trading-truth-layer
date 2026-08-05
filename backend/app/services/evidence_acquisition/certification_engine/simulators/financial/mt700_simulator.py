"""
MT700 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT700Simulator(BaseProviderSimulator):
    """
    MT700 documentary credit simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt700"

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
                "MT700 simulator is not connected."
            )

        return [
            {
                "message_type": "MT700",
                "credit_number": "LC-700001",
                "applicant": "TTL CAPITAL",
                "beneficiary": "GLOBAL SUPPLIER",
                "amount": 750000.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "MT700Simulator",
]