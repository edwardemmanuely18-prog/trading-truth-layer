"""
Trading Truth Layer (TTL)

Gateway Engine

FIX Protocol Adapter

Canonical FIX session adapter.
"""

from __future__ import annotations

import socket

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

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
class FIXSnapshot:

    gateways: List[Dict[str, Any]]

    accounts: List[Dict[str, Any]]

    instruments: List[Dict[str, Any]]

    positions: List[Dict[str, Any]]

    orders: List[Dict[str, Any]]

    executions: List[Dict[str, Any]]

    trades: List[Dict[str, Any]]

    market_data: List[Dict[str, Any]]

    errors: List[Dict[str, Any]]


# ============================================================================
# FIX Session State
# ============================================================================


class FIXSessionState(str, Enum):

    DISCONNECTED = "disconnected"

    CONNECTING = "connecting"

    LOGGING_ON = "logging_on"

    ACTIVE = "active"

    RECOVERING = "recovering"

    LOGGING_OUT = "logging_out"

    CLOSED = "closed"


# ============================================================================
# FIX Configuration
# ============================================================================


@dataclass(slots=True)
class FIXConfiguration:

    host: str

    port: int

    sender_comp_id: str

    target_comp_id: str

    begin_string: str = "FIX.4.4"

    heartbeat_interval: int = 30

    username: Optional[str] = None

    password: Optional[str] = None


# ============================================================================
# FIX Session
# ============================================================================


class FIXSession:
    """
    Canonical FIX session.

    Responsible only for FIX session management.

    It intentionally contains no broker-specific logic.
    """

    def __init__(

        self,

        configuration: FIXConfiguration,

    ):

        self.configuration = configuration

        self.state = FIXSessionState.DISCONNECTED

        self.socket: Optional[socket.socket] = None

        self.inbound_sequence = 1

        self.outbound_sequence = 1

        self.logged_on = False

        self.connected_at: Optional[datetime] = None

        #
        # Runtime evidence
        #

        self.accounts: List[Dict[str, Any]] = []

        self.positions: List[Dict[str, Any]] = []

        self.orders: List[Dict[str, Any]] = []

        self.executions: List[Dict[str, Any]] = []

        self.trades: List[Dict[str, Any]] = []

        self.instruments: List[Dict[str, Any]] = []

        self.market_data: Dict[str, Dict[str, Any]] = {}

        self.errors: List[Dict[str, Any]] = []


# ============================================================================
# FIX Adapter
# ============================================================================


class FIXAdapter(BaseGatewayAdapter):
    """
    Canonical FIX transport adapter.
    """

    def __init__(

        self,

        configuration: FIXConfiguration,

    ):

        super().__init__(

            provider_name="fix",

            gateway_type=GatewayType.FIX,

        )

        self.provider = ProviderDescriptor(

            provider_name="fix",

            gateway_type=GatewayType.FIX,

            display_name="FIX Protocol",

            vendor="FIX Trading Community",

            version="4.4",

        )

        self.configuration = configuration

        self.session = FIXSession(

            configuration,

        )

        self.connected_at: Optional[datetime] = None


# ============================================================================
# FIX Administrative Message Types
# ============================================================================

SOH = "\x01"


class FIXMessageType:

    HEARTBEAT = "0"

    TEST_REQUEST = "1"

    RESEND_REQUEST = "2"

    REJECT = "3"

    SEQUENCE_RESET = "4"

    LOGOUT = "5"

    LOGON = "A"

# ============================================================================
# Administrative Message Builder
# ============================================================================

    def _build_admin_message(
        self,
        message_type: str,
        fields: Dict[str, Any],
    ) -> str:

        message = {

            "35": message_type,

            "34": self.outbound_sequence,

            "49": self.configuration.sender_comp_id,

            "56": self.configuration.target_comp_id,

        }

        message.update(fields)

        body = SOH.join(
            f"{tag}={value}"
            for tag, value in message.items()
        )

        self.outbound_sequence += 1

        return body + SOH

# ============================================================================
# Logon
# ============================================================================

    def logon(self):

        self.state = FIXSessionState.LOGGING_ON

        fields = {

            "98": 0,

            "108": self.configuration.heartbeat_interval,

        }

        if self.configuration.username:

            fields["553"] = self.configuration.username

            fields["554"] = self.configuration.password or ""

        message = self._build_admin_message(

            FIXMessageType.LOGON,

            fields,

        )

        self.send(message)

        self.logged_on = True

        self.state = FIXSessionState.ACTIVE

# ============================================================================
# Heartbeat
# ============================================================================

    def heartbeat(self):

        message = self._build_admin_message(

            FIXMessageType.HEARTBEAT,

            {},

        )

        self.send(message)

# ============================================================================
# Test Request
# ============================================================================

    def test_request(

        self,

        request_id: str,

    ):

        message = self._build_admin_message(

            FIXMessageType.TEST_REQUEST,

            {

                "112": request_id,

            },

        )

        self.send(message)

# ============================================================================
# Resend Request
# ============================================================================

    def resend_request(

        self,

        begin_seq: int,

        end_seq: int,

    ):

        self.state = FIXSessionState.RECOVERING

        message = self._build_admin_message(

            FIXMessageType.RESEND_REQUEST,

            {

                "7": begin_seq,

                "16": end_seq,

            },

        )

        self.send(message)

# ============================================================================
# Logout
# ============================================================================

    def logout(self):

        self.state = FIXSessionState.LOGGING_OUT

        message = self._build_admin_message(

            FIXMessageType.LOGOUT,

            {},

        )

        self.send(message)

        self.logged_on = False

# ============================================================================
# Administrative Message Processing
# ============================================================================

    def process_admin_message(

        self,

        fields: Dict[str, str],

    ):

        message_type = fields.get("35")

        if message_type == FIXMessageType.HEARTBEAT:

            return

        if message_type == FIXMessageType.TEST_REQUEST:

            self.heartbeat()

            return

        if message_type == FIXMessageType.LOGOUT:

            self.logged_on = False

            self.state = FIXSessionState.CLOSED

            return

        if message_type == FIXMessageType.SEQUENCE_RESET:

            self.inbound_sequence = int(

                fields.get(

                    "36",

                    self.inbound_sequence,

                )

            )

            return

        if message_type == FIXMessageType.REJECT:

            return

# ============================================================================
# Lifecycle
# ============================================================================

    def initialize(self):

        self.mark_initialized()


    def connect(self):

        self.session.connect()

        self.session.logon()

        self.mark_connected()


    def disconnect(self):

        self.session.logout()

        self.session.disconnect()

        self.mark_disconnected()


# ============================================================================
# Application Message Types
# ============================================================================

class FIXApplicationMessageType:

    EXECUTION_REPORT = "8"

    ORDER_CANCEL_REJECT = "9"

    MARKET_DATA_SNAPSHOT = "W"

    MARKET_DATA_INCREMENTAL = "X"

    POSITION_REPORT = "AP"

    COLLATERAL_REPORT = "BA"

    SECURITY_LIST = "y"


# ============================================================================
# Runtime Evidence Store
# ============================================================================

    def reset_runtime(self):

        self.orders = []

        self.executions = []

        self.positions = []

        self.market_data = {}

        self.accounts = []

        self.errors = []


# ============================================================================
# FIX Parser
# ============================================================================

    @staticmethod
    def parse(raw_message: str) -> Dict[str, str]:

        fields = {}

        for field in raw_message.split(SOH):

            if "=" not in field:
                continue

            tag, value = field.split("=", 1)

            fields[tag] = value

        return fields


# ============================================================================
# Application Dispatcher
# ============================================================================

    def process_application_message(

        self,

        fields: Dict[str, str],

    ):

        message_type = fields.get("35")

        if message_type == FIXApplicationMessageType.EXECUTION_REPORT:

            self.executions.append(fields)

            return

        if message_type == FIXApplicationMessageType.POSITION_REPORT:

            self.positions.append(fields)

            return

        if message_type == FIXApplicationMessageType.MARKET_DATA_SNAPSHOT:

            symbol = fields.get("55")

            if symbol:

                self.market_data[symbol] = fields

            return

        if message_type == FIXApplicationMessageType.MARKET_DATA_INCREMENTAL:

            symbol = fields.get("55")

            if symbol:

                self.market_data[symbol] = fields

            return

        if message_type == FIXApplicationMessageType.ORDER_CANCEL_REJECT:

            self.errors.append(fields)

            return

        self.orders.append(fields)


# ============================================================================
# Receive Loop
# ============================================================================

    def receive_message(self):

        raw = self.receive()

        fields = self.parse(raw)

        message_type = fields.get("35")

        if message_type in {

            FIXMessageType.LOGON,

            FIXMessageType.LOGOUT,

            FIXMessageType.HEARTBEAT,

            FIXMessageType.TEST_REQUEST,

            FIXMessageType.RESEND_REQUEST,

            FIXMessageType.SEQUENCE_RESET,

            FIXMessageType.REJECT,

        }:

            self.process_admin_message(fields)

        else:

            self.process_application_message(fields)


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

                k: FIXAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                FIXAdapter._normalize(v)

                for v in value

            ]

        if hasattr(

            value,

            "__dict__",

        ):

            return {

                k: FIXAdapter._normalize(v)

                for k, v in vars(value).items()

            }

        return value


# ============================================================================
# Canonical Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(

        self,

    ) -> FIXSnapshot:

        gateways = [

            {

                "provider": self.provider_name,

                "gateway_type": self.gateway_type.value,

                "connected": self.is_connected,

                "transport": "tcp",

                "protocol": self.configuration.begin_string,

                "sender_comp_id": self.configuration.sender_comp_id,

                "target_comp_id": self.configuration.target_comp_id,

            }

        ]

        return FIXSnapshot(

            gateways=gateways,

            accounts=self._normalize(

                self.session.accounts,

            ),

            instruments=self._normalize(

                self.session.instruments,

            ),

            positions=self._normalize(

                self.session.positions,

            ),

            orders=self._normalize(

                self.session.orders,

            ),

            executions=self._normalize(

                self.session.executions,

            ),

            trades=self._normalize(

                self.session.trades,

            ),

            market_data=self._normalize(

                list(

                    self.session.market_data.values(),

                )

            ),

            errors=self._normalize(

                self.session.errors,

            ),

        )


# ============================================================================
# Public Acquisition
# ============================================================================


    def acquire(

        self,

    ) -> FIXSnapshot:

        try:

            snapshot = self._collect_snapshot()

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

                "fix_session": True,

                "streaming": True,

                "market_data": True,

                "orders": True,

                "positions": True,

                "executions": True,

                "trades": True,

                "sequence_recovery": True,

                "heartbeat": True,

                "logon": True,

                "logout": True,

                "historical_data": False,

                "transport": "tcp",

                "protocol": self.configuration.begin_string,

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

        diagnostics["fix"] = {

            "host": self.configuration.host,

            "port": self.configuration.port,

            "begin_string": self.configuration.begin_string,

            "sender_comp_id": self.configuration.sender_comp_id,

            "target_comp_id": self.configuration.target_comp_id,

            "session_state": self.session.state.value,

            "logged_on": self.session.logged_on,

            "connected": self.is_connected,

            "inbound_sequence":

                self.session.inbound_sequence,

            "outbound_sequence":

                self.session.outbound_sequence,

            "accounts":

                len(self.session.accounts),

            "instruments":

                len(self.session.instruments),

            "positions":

                len(self.session.positions),

            "orders":

                len(self.session.orders),

            "executions":

                len(self.session.executions),

            "trades":

                len(self.session.trades),

            "market_data":

                len(self.session.market_data),

            "errors":

                len(self.session.errors),

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

    "FIXSnapshot",

    "FIXSessionState",

    "FIXConfiguration",

    "FIXSession",

    "FIXAdapter",

]