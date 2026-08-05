"""
MT767 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT767Simulator(BaseProviderSimulator):
    """
    MT767 guarantee amendment simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt767"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "bic",
            "session",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "MT767 simulator is not connected."
            )

        return [
            {
                "message_type": "MT767",
                "amendment_reference": "AMD-767001",
                "related_guarantee": "BG-760001",
                "status": "AMENDED",
            }
        ]


__all__ = [
    "MT767Simulator",
]