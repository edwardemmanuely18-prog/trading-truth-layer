"""
NinjaTrader Gateway simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class NinjaTraderGatewaySimulator(BaseProviderSimulator):

    @property
    def provider_name(self) -> str:
        return "ninjatrader_gateway"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return {"username", "password"}.issubset(credentials)

    def synchronize(self) -> List[Dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("NinjaTrader Gateway simulator is not connected.")

        return [{
            "gateway": "NinjaTrader",
            "connections": 2,
            "executions": 24,
        }]


__all__ = ["NinjaTraderGatewaySimulator"]