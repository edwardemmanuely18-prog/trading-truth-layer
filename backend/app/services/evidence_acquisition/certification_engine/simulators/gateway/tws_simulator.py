"""
TWS simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class TWSSimulator(BaseProviderSimulator):
    """
    Trader Workstation gateway simulator.
    """

    @property
    def provider_name(self) -> str:
        return "tws"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "host",
            "port",
            "client_id",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "TWS simulator is not connected."
            )

        return [
            {
                "gateway": "Trader Workstation",
                "account": "DU123456",
                "executions": 12,
            }
        ]


__all__ = [
    "TWSSimulator",
]