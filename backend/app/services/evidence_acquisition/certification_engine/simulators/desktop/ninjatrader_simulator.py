"""
NinjaTrader simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class NinjaTraderSimulator(BaseProviderSimulator):
    """
    NinjaTrader provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "ninjatrader"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "NinjaTrader simulator is not connected."
            )

        return [
            {
                "execution_id": "NT-10001",
                "instrument": "ESU26",
                "side": "BUY",
                "quantity": 2,
                "entry_price": 6498.25,
                "exit_price": 6502.75,
                "profit": 450.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "NinjaTraderSimulator",
]