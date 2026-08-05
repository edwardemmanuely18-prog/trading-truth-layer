"""
MT5 Gateway simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT5GatewaySimulator(BaseProviderSimulator):
    """
    MT5 Gateway simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt5_gateway"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "server",
            "login",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "MT5 Gateway simulator is not connected."
            )

        return [
            {
                "gateway": "MetaTrader 5",
                "server": "TTL-Demo",
                "sessions": 1,
                "accounts": 5,
            }
        ]


__all__ = [
    "MT5GatewaySimulator",
]