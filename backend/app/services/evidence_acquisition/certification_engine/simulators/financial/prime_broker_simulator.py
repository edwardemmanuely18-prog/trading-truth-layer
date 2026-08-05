"""
Prime Broker simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class PrimeBrokerSimulator(BaseProviderSimulator):
    """
    Prime Broker provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "prime_broker"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "broker_id",
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Prime Broker simulator is not connected."
            )

        return [
            {
                "account": "PB-10001",
                "margin_balance": 2500000.00,
                "equity": 3150000.00,
                "buying_power": 9450000.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "PrimeBrokerSimulator",
]