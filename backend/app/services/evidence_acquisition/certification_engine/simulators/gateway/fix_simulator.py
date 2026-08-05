"""
FIX simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class FixSimulator(BaseProviderSimulator):
    """
    FIX protocol simulator.
    """

    @property
    def provider_name(self) -> str:
        return "fix"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "sender_comp_id",
            "target_comp_id",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "FIX simulator is not connected."
            )

        return [
            {
                "begin_string": "FIX.4.4",
                "msg_type": "8",
                "exec_id": "FIX-100001",
                "symbol": "EUR/USD",
                "side": "BUY",
                "quantity": 100000,
                "price": 1.10320,
            }
        ]


__all__ = [
    "FixSimulator",
]