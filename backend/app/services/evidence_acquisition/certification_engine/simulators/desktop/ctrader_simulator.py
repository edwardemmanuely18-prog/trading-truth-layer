"""
cTrader simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class CTraderSimulator(BaseProviderSimulator):
    """
    cTrader provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "ctrader"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "account_id",
            "access_token",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "cTrader simulator is not connected."
            )

        return [
            {
                "position_id": 55001,
                "symbol": "EURUSD",
                "side": "SELL",
                "volume": 2.00,
                "entry_price": 1.10520,
                "exit_price": 1.10310,
                "profit": 420.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "CTraderSimulator",
]