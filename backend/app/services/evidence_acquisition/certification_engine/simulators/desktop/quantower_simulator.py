"""
Quantower simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class QuantowerSimulator(BaseProviderSimulator):
    """
    Quantower provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "quantower"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "workspace",
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Quantower simulator is not connected."
            )

        return [
            {
                "execution_id": "QT-10001",
                "symbol": "XAUUSD",
                "side": "BUY",
                "quantity": 2,
                "price": 3360.40,
                "currency": "USD",
            }
        ]


__all__ = [
    "QuantowerSimulator",
]