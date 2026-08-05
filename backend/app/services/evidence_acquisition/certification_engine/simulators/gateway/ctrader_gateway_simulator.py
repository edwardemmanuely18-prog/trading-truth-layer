"""
cTrader Gateway simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class CTraderGatewaySimulator(BaseProviderSimulator):
    """
    cTrader Gateway simulator.
    """

    @property
    def provider_name(self) -> str:
        return "ctrader_gateway"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "client_id",
            "client_secret",
            "access_token",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "cTrader Gateway simulator is not connected."
            )

        return [
            {
                "gateway": "cTrader",
                "workspace": "Demo",
                "positions": 8,
                "orders": 14,
            }
        ]


__all__ = [
    "CTraderGatewaySimulator",
]