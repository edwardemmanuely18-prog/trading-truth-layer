"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT KYC Registry Client

Institutional client for the SWIFT KYC Registry API.

Responsibilities
----------------
• Retrieve institution profiles
• Retrieve counterparty profiles
• Retrieve supporting documents
• Retrieve entity information
• Submit access requests
• Normalize KYC responses

This client acquires native KYC Registry data only.

Translation into canonical Financial Evidence is delegated
to the Financial Engine.
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
    KYC,
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
class KYCConfiguration:

    base_url: str

    timeout: int = 30


# ============================================================================
# Client
# ============================================================================


class KYCClient:
    """
    SWIFT KYC Registry client.
    """

    def __init__(
        self,
        configuration: KYCConfiguration,
        authentication: SwiftAuthentication,
    ) -> None:

        self.configuration = configuration

        self.authentication = authentication

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(
        self,
        endpoint: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> List[ISO20022Message]:

        url = (
            self.configuration.base_url
            + endpoint
        )

        response = requests.get(

            url,

            headers={
                **self.authentication.authorization_header,
                "Accept": "application/json",
            },

            params=params,

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

    def _post(
        self,
        endpoint: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:

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

        return response.json()

    # ------------------------------------------------------------------
    # Institution Directory
    # ------------------------------------------------------------------

    def institutions(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "kyc",

            KYC["institutions"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Entity Profile
    # ------------------------------------------------------------------

    def institution(
        self,
        bic: str,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "kyc",

            KYC["institution"].format(
                bic=bic,
            ),
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Supporting Documents
    # ------------------------------------------------------------------

    def documents(
        self,
        bic: str,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "kyc",

            KYC["documents"].format(
                bic=bic,
            ),
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Access Request
    # ------------------------------------------------------------------

    def request_access(
        self,
        my_entity: str,
        counterparty_entity: str,
        due_diligence_level: str = "BASIC",
        note: Optional[str] = None,
    ) -> Dict[str, Any]:

        endpoint = (
            "/kycr/v5/accesses/request"
        )

        body = {

            "myEntity": my_entity,

            "counterpartyEntity": counterparty_entity,

            "dueDiligenceLevel": due_diligence_level,
        }

        if note:

            body["note"] = note

        return self._post(
            endpoint,
            body,
        )

    # ------------------------------------------------------------------
    # Canonical Financial Builders
    # ------------------------------------------------------------------

    def institution_directory(
        self,
    ):
        """
        Return the SWIFT institution directory.
        """

        return self.institutions()


    def financial_institutions(
        self,
    ):
        """
        Canonical financial institution evidence.
        """

        return self.institutions()


    def counterparties(
        self,
    ):
        """
        Canonical counterparty evidence.

        Counterparties originate from the KYC Registry.
        """

        return self.institutions()


    def institution_documents(
        self,
        bic: str,
    ):
        """
        Supporting institution documentation.
        """

        return self.documents(
            bic,
        )


    def due_diligence_documents(
        self,
        bic: str,
    ):
        """
        Canonical due diligence evidence.
        """

        return self.documents(
            bic,
        )


    def beneficial_ownership(
        self,
    ):
        """
        Beneficial ownership evidence.

        Not currently exposed through this client.
        """

        return []


    def sanctions_screening(
        self,
    ):
        """
        Sanctions screening evidence.

        Provided by the Compliance client.
        """

        return []


    def kyc_profiles(
        self,
    ):
        """
        Canonical KYC profile evidence.
        """

        return self.institutions()

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def synchronize(
        self,
    ) -> List[ISO20022Message]:

        evidence = []

        evidence.extend(
            self.institutions()
        )

        return evidence


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "KYCConfiguration",

    "KYCClient",
]