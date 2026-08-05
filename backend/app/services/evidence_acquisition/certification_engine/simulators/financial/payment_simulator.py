"""
Payment simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class PaymentSimulator(BaseProviderSimulator):
    """
    Payment provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "payment"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "api_key",
            "merchant_id",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Payment simulator is not connected."
            )

        return [
            {
                "payment_id": "PAY-100001",
                "amount": 25000.00,
                "currency": "USD",
                "status": "COMPLETED",
                "beneficiary": "TTL CAPITAL",
            }
        ]


__all__ = [
    "PaymentSimulator",
]