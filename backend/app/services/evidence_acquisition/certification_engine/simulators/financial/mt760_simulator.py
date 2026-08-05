"""
MT760 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT760Simulator(BaseProviderSimulator):
    """
    MT760 guarantee simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt760"

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
                "MT760 simulator is not connected."
            )

        return [
            {
                "message_type": "MT760",
                "guarantee_reference": "BG-760001",
                "applicant": "TTL CAPITAL",
                "beneficiary": "GLOBAL BENEFICIARY",
                "amount": 1500000.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "MT760Simulator",
]