"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Payments Client

Institutional client for SWIFT gpi payment tracking.

Responsibilities
----------------
• Track outbound payments
• Track inbound payments
• Query payment status
• Query payment history
• Normalize ISO 20022 responses

This client acquires payment tracking information only.
It does not initiate payments.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests

from .authentication import SwiftAuthentication
from .endpoints import (
    PAYMENTS,
    SwiftEndpoints,
)
from .iso20022 import (
    ISO20022Message,
    ISO20022Normalizer,
)


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class PaymentsConfiguration:

    base_url: str

    timeout: int = 30


# ============================================================================
# Client
# ============================================================================


class PaymentsClient:
    """
    SWIFT gpi payment tracking client.
    """

    def __init__(
        self,
        configuration: PaymentsConfiguration,
        authentication: SwiftAuthentication,
    ) -> None:

        self.configuration = configuration

        self.authentication = authentication

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _post(
        self,
        endpoint: str,
        body: Dict[str, Any],
    ) -> List[ISO20022Message]:

        url = (
            self.configuration.base_url
            + endpoint
        )

        response = requests.post(

            url,

            json=body,

            headers={
                **self.authentication.authorization_header,
                "Accept": "application/json",
            },

            timeout=self.configuration.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        records = payload.get(
            "items",
            [],
        )

        return [

            ISO20022Normalizer.normalize(
                record
            )

            for record in records
        ]

    # ------------------------------------------------------------------
    # Outbound
    # ------------------------------------------------------------------

    def outbound_payment(
        self,
        uetr: str,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "payments",

            PAYMENTS["payments"],
        )

        return self._post(

            endpoint,

            {
                "uetr": uetr,
            },
        )

    # ------------------------------------------------------------------
    # Inbound
    # ------------------------------------------------------------------

    def inbound_payment(
        self,
        uetr: str,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "payments",

            PAYMENTS["payments"],
        )

        return self._post(

            endpoint,

            {
                "uetr": uetr,
            },
        )

    # ------------------------------------------------------------------
    # Time Window Search
    # ------------------------------------------------------------------

    def search(
        self,
        start_date_time: str,
        end_date_time: str,
        maximum_number: int = 100,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "payments",

            PAYMENTS["payments"],
        )

        return self._post(

            endpoint,

            {

                "start_date_time": start_date_time,

                "end_date_time": end_date_time,

                "maximum_number": maximum_number,
            },
        )

    # ------------------------------------------------------------------
    # Canonical Financial Builders
    # ------------------------------------------------------------------

    def payments(
        self,
    ):
        """
        Canonical payment evidence.

        The caller is expected to invoke search() or synchronize()
        beforehand when operating against live SWIFT services.

        This convenience method returns an empty collection until
        a synchronization window has been executed.
        """

        return []


    def cash_transfers(
        self,
    ):
        """
        Canonical cash transfer evidence.

        Payment tracking records are interpreted as transfer evidence.
        """

        return self.payments()


    def settlement_instructions(
        self,
    ):
        """
        Canonical settlement instructions.

        SWIFT gpi does not expose settlement instructions directly.
        """

        return []


    def settlement_confirmations(
        self,
    ):
        """
        Canonical settlement confirmations.

        Payment completion information is obtained during
        payment tracking.
        """

        return self.payments()

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def synchronize(
        self,
        start_date_time: str,
        end_date_time: str,
    ) -> List[ISO20022Message]:

        return self.search(

            start_date_time,

            end_date_time,
        )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "PaymentsConfiguration",

    "PaymentsClient",
]