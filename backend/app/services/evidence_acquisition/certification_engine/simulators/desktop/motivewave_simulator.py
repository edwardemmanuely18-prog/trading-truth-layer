"""
MotiveWave simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MotiveWaveSimulator(BaseProviderSimulator):
    """
    MotiveWave provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "motivewave"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "license_key",
            "username",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "MotiveWave simulator is not connected."
            )

        return [
            {
                "execution_id": "MW-10001",
                "symbol": "XAGUSD",
                "side": "SELL",
                "quantity": 5,
                "price": 38.42,
                "currency": "USD",
            }
        ]


__all__ = [
    "MotiveWaveSimulator",
]