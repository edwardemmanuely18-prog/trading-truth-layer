"""
gRPC simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class GrpcSimulator(BaseProviderSimulator):
    """
    gRPC simulator.
    """

    @property
    def provider_name(self) -> str:
        return "grpc"

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
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "gRPC simulator is not connected."
            )

        return [
            {
                "service": "TradeService",
                "rpc": "GetExecutions",
                "responses": 20,
            }
        ]


__all__ = [
    "GrpcSimulator",
]