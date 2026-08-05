"""
Trading Truth Layer (TTL)

Gateway Engine

Generic REST Adapter

Canonical provider-agnostic REST transport adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests

from ..models import (
    GatewayType,
)

from ..registry import (
    ProviderDescriptor,
)

from .base_adapter import (
    BaseGatewayAdapter,
)


# ============================================================================
# Canonical Snapshot
# ============================================================================


@dataclass(slots=True)
class RESTSnapshot:

    gateways: List[Dict[str, Any]]

    responses: List[Any]

    errors: List[Any]


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class RESTConfiguration:

    base_url: str

    headers: Dict[str, str] = field(
        default_factory=dict,
    )

    authentication: Optional[str] = None

    timeout: int = 30

    verify_ssl: bool = True

    environment: str = "rest"

    provider_name: str = "rest"


# ============================================================================
# Runtime State
# ============================================================================


class RESTState(str, Enum):

    DISCONNECTED = "disconnected"

    CONNECTING = "connecting"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# REST Adapter
# ============================================================================


class RESTAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: RESTConfiguration,

    ):

        super().__init__(

            provider_name=configuration.provider_name,

            gateway_type=GatewayType.REST,

        )

        self.provider = ProviderDescriptor(

            provider_name=configuration.provider_name,

            gateway_type=GatewayType.REST,

            display_name="Generic REST",

            vendor="Trading Truth Layer",

            version="1.0",

        )

        self.configuration = configuration

        self.state = RESTState.DISCONNECTED

        self.session = requests.Session()

        self.session.headers.update(

            configuration.headers,

        )

        self.responses: List[Any] = []

        self.errors: List[Any] = []

        self.connected_at: Optional[datetime] = None


# ============================================================================
# Lifecycle
# ============================================================================


    def initialize(
        self,
    ) -> None:

        self.mark_initialized()


    def connect(
        self,
    ) -> None:

        self.state = RESTState.CONNECTING

        if self.configuration.authentication:

            self.session.headers[

                "Authorization"

            ] = self.configuration.authentication

        self.state = RESTState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        self.session.close()

        self.state = RESTState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# HTTP Operations
# ============================================================================


    def get(

        self,

        endpoint: str,

        params: Optional[Dict[str, Any]] = None,

    ):

        response = self.session.get(

            self.configuration.base_url + endpoint,

            params=params,

            timeout=self.configuration.timeout,

            verify=self.configuration.verify_ssl,

        )

        response.raise_for_status()

        return response.json()


    def post(

        self,

        endpoint: str,

        payload: Optional[Dict[str, Any]] = None,

    ):

        response = self.session.post(

            self.configuration.base_url + endpoint,

            json=payload,

            timeout=self.configuration.timeout,

            verify=self.configuration.verify_ssl,

        )

        response.raise_for_status()

        return response.json()


    def put(

        self,

        endpoint: str,

        payload: Optional[Dict[str, Any]] = None,

    ):

        response = self.session.put(

            self.configuration.base_url + endpoint,

            json=payload,

            timeout=self.configuration.timeout,

            verify=self.configuration.verify_ssl,

        )

        response.raise_for_status()

        return response.json()


    def delete(

        self,

        endpoint: str,

    ):

        response = self.session.delete(

            self.configuration.base_url + endpoint,

            timeout=self.configuration.timeout,

            verify=self.configuration.verify_ssl,

        )

        response.raise_for_status()

        return response.json()


# ============================================================================
# Normalization
# ============================================================================


    @staticmethod
    def _normalize(

        value,

    ):

        if value is None:

            return None

        if isinstance(

            value,

            dict,

        ):

            return {

                k: RESTAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                RESTAdapter._normalize(v)

                for v in value

            ]

        if hasattr(

            value,

            "__dict__",

        ):

            return {

                k: RESTAdapter._normalize(v)

                for k, v in vars(value).items()

            }

        return value


# ============================================================================
# Canonical Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(

        self,

        endpoint: str,

        params: Optional[Dict[str, Any]] = None,

    ) -> RESTSnapshot:

        response = self.get(

            endpoint,

            params=params,

        )

        evidence = self._normalize(

            response,

        )

        self.responses.append(

            evidence,

        )

        return RESTSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "https",

                    "protocol": "rest",

                }

            ],

            responses=list(

                self.responses,

            ),

            errors=list(

                self.errors,

            ),

        )


# ============================================================================
# Public Acquisition
# ============================================================================


    def acquire(

        self,

        endpoint: str,

        params: Optional[Dict[str, Any]] = None,

    ) -> RESTSnapshot:

        try:

            snapshot = self._collect_snapshot(

                endpoint,

                params,

            )

            self.record_acquisition()

            return snapshot

        except Exception as exc:

            self.record_failure(

                exc,

            )

            raise


# ============================================================================
# Capabilities
# ============================================================================


    def capabilities(
        self,
    ) -> Dict[str, Any]:

        capabilities = super().capabilities()

        capabilities.update(

            {

                "provider_name": self.provider_name,

                "gateway_type": self.gateway_type.value,

                "rest": True,

                "https": True,

                "json": True,

                "get": True,

                "post": True,

                "put": True,

                "delete": True,

                "provider_agnostic": True,

                "gateway": True,

            }

        )

        return capabilities


# ============================================================================
# Diagnostics
# ============================================================================


    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        diagnostics = super().diagnostics()

        diagnostics["rest"] = {

            "provider": self.provider_name,

            "base_url": self.configuration.base_url,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "verify_ssl": self.configuration.verify_ssl,

            "timeout": self.configuration.timeout,

            "responses": len(self.responses),

            "errors": len(self.errors),

        }

        return diagnostics


# ============================================================================
# Cleanup
# ============================================================================


    def close(
        self,
    ) -> None:

        if self.is_connected:

            self.disconnect()

        self.mark_closed()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "RESTSnapshot",

    "RESTConfiguration",

    "RESTState",

    "RESTAdapter",

]