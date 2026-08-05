"""
TradeStation simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class TradeStationSimulator(BaseProviderSimulator):
    """
    TradeStation provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "tradestation"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

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
                "TradeStation simulator is not connected."
            )

        return [
            {
                "trade_id": "TS-10001",
                "symbol": "AAPL",
                "asset_class": "STOCK",
                "side": "BUY",
                "quantity": 100,
                "price": 245.60,
                "currency": "USD",
            }
        ]


__all__ = [
    "TradeStationSimulator",
]