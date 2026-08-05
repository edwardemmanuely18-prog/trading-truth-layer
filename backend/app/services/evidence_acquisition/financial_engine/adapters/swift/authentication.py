"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Authentication

Institutional authentication layer for all SWIFT APIs.

Responsibilities
----------------
• OAuth token acquisition
• Token lifecycle management
• Token refresh
• Authorization header generation
• Authentication state reporting

Every SWIFT API client should use this class rather than
implementing authentication independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import Optional

import requests


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class SwiftAuthenticationConfiguration:
    """
    SWIFT OAuth configuration.
    """

    token_url: str

    client_id: str

    client_secret: str

    scope: Optional[str] = None

    timeout: int = 30


# ============================================================================
# Token
# ============================================================================


@dataclass(slots=True)
class SwiftAccessToken:
    """
    OAuth access token.
    """

    access_token: str

    token_type: str

    expires_at: datetime

    scope: Optional[str] = None

    @property
    def expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at

    @property
    def authorization_header(self) -> Dict[str, str]:
        return {
            "Authorization": f"{self.token_type} {self.access_token}"
        }


# ============================================================================
# Authentication
# ============================================================================


class SwiftAuthentication:
    """
    Canonical SWIFT authentication service.
    """

    def __init__(
        self,
        configuration: SwiftAuthenticationConfiguration,
    ) -> None:

        self.configuration = configuration

        self._token: Optional[
            SwiftAccessToken
        ] = None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> SwiftAccessToken:
        """
        Acquire a new OAuth access token.
        """

        response = requests.post(

            self.configuration.token_url,

            data={
                "grant_type": "client_credentials",
            },

            auth=(
                self.configuration.client_id,
                self.configuration.client_secret,
            ),

            timeout=self.configuration.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        expires = datetime.utcnow() + timedelta(
            seconds=payload["expires_in"]
        )

        self._token = SwiftAccessToken(

            access_token=payload["access_token"],

            token_type=payload.get(
                "token_type",
                "Bearer",
            ),

            expires_at=expires,

            scope=payload.get("scope"),
        )

        return self._token

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(self) -> SwiftAccessToken:

        return self.authenticate()

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    @property
    def token(self) -> SwiftAccessToken:

        if self._token is None:

            return self.authenticate()

        if self._token.expired:

            return self.refresh()

        return self._token

    @property
    def authorization_header(self) -> Dict[str, str]:

        return self.token.authorization_header

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def authenticated(self) -> bool:

        return self._token is not None

    @property
    def expires_at(self) -> Optional[datetime]:

        if self._token is None:

            return None

        return self._token.expires_at

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:

        self._token = None


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "SwiftAuthenticationConfiguration",
    "SwiftAccessToken",
    "SwiftAuthentication",
]