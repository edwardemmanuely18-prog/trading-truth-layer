"""
Custodian simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class CustodianSimulator(BaseProviderSimulator):
    """
    Custodian provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "custodian"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "custodian_id",
            "api_key",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Custodian simulator is not connected."
            )

        return [
            {
                "portfolio_id": "PF-10001",
                "asset": "US Treasury Bond",
                "quantity": 1000,
                "market_value": 1012500.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "CustodianSimulator",
]