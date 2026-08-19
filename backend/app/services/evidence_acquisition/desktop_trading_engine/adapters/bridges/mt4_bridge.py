"""
Trading Truth Layer (TTL)
Universal Evidence Adapter (UEA)

MetaTrader 4 Bridge

Responsibilities
----------------
The MT4 bridge is intentionally thin.

It owns only:

    • endpoint configuration
    • session identity
    • HTTP transport
    • request/response correlation
    • handshake
    • heartbeat
    • connection state
    • provider-operation wrappers

It does NOT own:

    • evidence normalization
    • canonical Desktop models
    • verification decisions
    • translation
    • synchronization
    • business logic

Those responsibilities remain in MT4Adapter and the shared
Desktop Trading Engine.
"""

from __future__ import annotations

import json
import os
import ssl
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class MT4BridgeError(RuntimeError):
    """Base MT4 bridge error."""


class MT4BridgeConnectionError(MT4BridgeError):
    """Raised when the bridge endpoint cannot be reached."""


class MT4BridgeProtocolError(MT4BridgeError):
    """Raised when the bridge response violates the protocol."""


@dataclass
class _PendingBridgeRequest:
    request: dict[str, Any]
    event: threading.Event = field(
        default_factory=threading.Event,
    )
    response: dict[str, Any] | None = None


@dataclass
class _MT4BridgeSession:
    session_id: str
    account: str | None
    server: str | None
    environment: str
    terminal: dict[str, Any] = field(
        default_factory=dict,
    )
    connected: bool = True
    last_seen: float = field(
        default_factory=time.time,
    )
    pending: dict[
        str,
        _PendingBridgeRequest,
    ] = field(
        default_factory=dict,
    )


_MT4_SESSIONS: dict[
    str,
    _MT4BridgeSession,
] = {}

_MT4_SESSIONS_LOCK = threading.RLock()

_MT4_BRIDGE_WAIT_SECONDS = 12.0


def _bridge_error(
    *,
    request_id: str,
    operation: str,
    code: str,
    message: str,
) -> dict[str, Any]:
    return {
        "protocol_version": MT4Bridge.PROTOCOL_VERSION,
        "request_id": request_id,
        "operation": operation,
        "ok": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _bridge_success(
    *,
    request_id: str,
    operation: str,
    data: Any = None,
) -> dict[str, Any]:
    return {
        "protocol_version": MT4Bridge.PROTOCOL_VERSION,
        "request_id": request_id,
        "operation": operation,
        "ok": True,
        "data": data,
        "error": None,
    }


def _find_mt4_session(
    *,
    session_id: str | None = None,
    account: str | None = None,
    server: str | None = None,
    environment: str | None = None,
) -> _MT4BridgeSession | None:

    now = time.time()

    with _MT4_SESSIONS_LOCK:

        if session_id:
            session = _MT4_SESSIONS.get(
                session_id
            )

            if session is not None:
                if (
                    now - session.last_seen
                    <= 30.0
                ):
                    return session

                session.connected = False

        candidates = []

        for session in _MT4_SESSIONS.values():

            if not session.connected:
                continue

            if (
                now - session.last_seen
                > 30.0
            ):
                session.connected = False
                continue

            if (
                account
                and session.account
                and str(session.account)
                != str(account)
            ):
                continue

            if (
                server
                and session.server
                and session.server.lower()
                != str(server).lower()
            ):
                continue

            if (
                environment
                and session.environment
                != environment
            ):
                continue

            candidates.append(session)

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: item.last_seen,
        )


def _register_mt4_terminal(
    *,
    request_id: str,
    session_id: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:

    account = payload.get(
        "account"
    )

    server = payload.get(
        "server"
    )

    environment = (
        payload.get(
            "environment",
            "development",
        )
        or "development"
    ).strip().lower()

    with _MT4_SESSIONS_LOCK:

        resolved_session_id = (
            session_id
            or str(uuid4())
        )

        session = _MT4_SESSIONS.get(
            resolved_session_id
        )

        if session is None:
            session = _MT4BridgeSession(
                session_id=resolved_session_id,
                account=(
                    str(account)
                    if account is not None
                    else None
                ),
                server=(
                    str(server)
                    if server is not None
                    else None
                ),
                environment=environment,
            )

            _MT4_SESSIONS[
                resolved_session_id
            ] = session

        session.connected = True
        session.last_seen = time.time()

        if account is not None:
            session.account = str(account)

        if server:
            session.server = str(server)

        session.environment = environment

        session.terminal = {
            "terminal": payload.get(
                "terminal"
            ),
            "terminal_build": payload.get(
                "terminal_build"
            ),
            "terminal_path": payload.get(
                "terminal_path"
            ),
        }

    return _bridge_success(
        request_id=request_id,
        operation="heartbeat",
        data={
            "session_id": resolved_session_id,
            "account": session.account,
            "server": session.server,
            "environment": session.environment,
            "terminal": session.terminal,
        },
    )


def _poll_mt4_terminal(
    *,
    request_id: str,
    session_id: str | None,
) -> dict[str, Any]:

    session = _find_mt4_session(
        session_id=session_id,
    )

    if session is None:
        return _bridge_error(
            request_id=request_id,
            operation="poll",
            code="MT4_SESSION_NOT_FOUND",
            message=(
                "MT4 bridge session was not found "
                "or is no longer active."
            ),
        )

    with _MT4_SESSIONS_LOCK:
        session.last_seen = time.time()

        pending = next(
            iter(
                session.pending.values()
            ),
            None,
        )

        if pending is None:
            return _bridge_success(
                request_id=request_id,
                operation="poll",
                data=None,
            )

        return _bridge_success(
            request_id=request_id,
            operation="poll",
            data=pending.request,
        )


def _receive_mt4_response(
    *,
    request_id: str,
    session_id: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:

    session = _find_mt4_session(
        session_id=session_id,
    )

    if session is None:
        return _bridge_error(
            request_id=request_id,
            operation="response",
            code="MT4_SESSION_NOT_FOUND",
            message="MT4 bridge session was not found.",
        )

    response_request_id = payload.get(
        "request_id"
    )

    if not response_request_id:
        return _bridge_error(
            request_id=request_id,
            operation="response",
            code="MT4_REQUEST_ID_MISSING",
            message="MT4 response request_id is missing.",
        )

    with _MT4_SESSIONS_LOCK:

        pending = session.pending.get(
            str(response_request_id)
        )

        if pending is None:
            return _bridge_error(
                request_id=request_id,
                operation="response",
                code="MT4_PENDING_REQUEST_NOT_FOUND",
                message=(
                    "No pending MT4 request exists "
                    f"for {response_request_id}."
                ),
            )

        pending.response = payload
        pending.event.set()

    return _bridge_success(
        request_id=request_id,
        operation="response",
        data={
            "accepted": True,
            "request_id": response_request_id,
        },
    )


def handle_mt4_bridge_message(
    message: dict[str, Any],
    *,
    authorization: str | None = None,
) -> dict[str, Any]:
    """
    Server-side bridge rendezvous handler.

    This function contains transport/session mechanics only.
    It does not acquire, normalize, verify, translate or
    synchronize evidence.
    """

    configured_token = os.getenv(
        "MT4_BRIDGE_TOKEN",
        "",
    ).strip()

    if configured_token:
        expected = (
            f"Bearer {configured_token}"
        )

        if authorization != expected:
            return _bridge_error(
                request_id=str(
                    message.get(
                        "request_id",
                        "",
                    )
                ),
                operation=str(
                    message.get(
                        "operation",
                        "unknown",
                    )
                ),
                code="MT4_BRIDGE_UNAUTHORIZED",
                message=(
                    "Invalid MT4 bridge authorization."
                ),
            )

    protocol_version = message.get(
        "protocol_version"
    )

    request_id = str(
        message.get(
            "request_id",
            "",
        )
    )

    operation = str(
        message.get(
            "operation",
            "",
        )
    )

    role = str(
        message.get(
            "role",
            "",
        )
    ).lower()

    session_id = message.get(
        "session_id"
    )

    payload = message.get(
        "payload"
    ) or {}

    if protocol_version != MT4Bridge.PROTOCOL_VERSION:
        return _bridge_error(
            request_id=request_id,
            operation=operation,
            code="MT4_PROTOCOL_VERSION_UNSUPPORTED",
            message=(
                f"Unsupported protocol version: "
                f"{protocol_version!r}"
            ),
        )

    if role == "terminal":

        if operation == "heartbeat":
            return _register_mt4_terminal(
                request_id=request_id,
                session_id=(
                    str(session_id)
                    if session_id
                    else None
                ),
                payload=payload,
            )

        if operation == "poll":
            return _poll_mt4_terminal(
                request_id=request_id,
                session_id=(
                    str(session_id)
                    if session_id
                    else None
                ),
            )

        if operation == "response":
            return _receive_mt4_response(
                request_id=request_id,
                session_id=(
                    str(session_id)
                    if session_id
                    else None
                ),
                payload=payload,
            )

        return _bridge_error(
            request_id=request_id,
            operation=operation,
            code="MT4_TERMINAL_OPERATION_UNSUPPORTED",
            message=(
                f"Unsupported terminal operation: "
                f"{operation}"
            ),
        )

    if role != "client":

        return _bridge_error(
            request_id=request_id,
            operation=operation,
            code="MT4_BRIDGE_ROLE_INVALID",
            message=(
                "Bridge message role must be "
                "'client' or 'terminal'."
            ),
        )

    account = payload.get(
        "account"
    )

    server = payload.get(
        "server"
    )

    environment = (
        payload.get(
            "environment",
        )
        or "development"
    ).strip().lower()

    session = _find_mt4_session(
        session_id=(
            str(session_id)
            if session_id
            else None
        ),
        account=(
            str(account)
            if account is not None
            else None
        ),
        server=server,
        environment=environment,
    )

    if session is None:
        return _bridge_error(
            request_id=request_id,
            operation=operation,
            code="MT4_TERMINAL_NOT_CONNECTED",
            message=(
                "No active MT4 terminal bridge session "
                "matches the configured account/server."
            ),
        )

    pending = _PendingBridgeRequest(
        request=message,
    )

    with _MT4_SESSIONS_LOCK:
        session.pending[
            request_id
        ] = pending
        session.last_seen = time.time()

    completed = pending.event.wait(
        timeout=_MT4_BRIDGE_WAIT_SECONDS
    )

    with _MT4_SESSIONS_LOCK:
        session.pending.pop(
            request_id,
            None,
        )

    if not completed:
        return _bridge_error(
            request_id=request_id,
            operation=operation,
            code="MT4_TERMINAL_RESPONSE_TIMEOUT",
            message=(
                "The MT4 terminal did not respond "
                "within the bridge timeout."
            ),
        )

    response = pending.response

    if not isinstance(
        response,
        dict,
    ):
        return _bridge_error(
            request_id=request_id,
            operation=operation,
            code="MT4_TERMINAL_RESPONSE_INVALID",
            message=(
                "The MT4 terminal returned an invalid response."
            ),
        )

    response_operation = response.get(
        "operation"
    )

    if response_operation != operation:
        return _bridge_error(
            request_id=request_id,
            operation=operation,
            code="MT4_OPERATION_MISMATCH",
            message=(
                "MT4 terminal response operation does "
                "not match the requested operation."
            ),
        )

    return {
        "protocol_version": MT4Bridge.PROTOCOL_VERSION,
        "request_id": request_id,
        "operation": operation,
        "ok": bool(
            response.get(
                "ok",
                False,
            )
        ),
        "data": response.get(
            "data"
        ),
        "error": response.get(
            "error"
        ),
    }



class MT4Bridge:

    PROTOCOL_VERSION = "1.0"
    BRIDGE_VERSION = "1.0"

    DEFAULT_LOCAL_ENDPOINT = (
        "http://127.0.0.1:8001/api/evidence-acquisition/mt4-bridge"
    )

    DEFAULT_PRODUCTION_ENDPOINT = os.getenv(
        "MT4_BRIDGE_PRODUCTION_ENDPOINT",
        "https://www.tradingtruthlayer.com/api/evidence-acquisition/mt4-bridge",
    )

    OPERATIONS = frozenset(
        {
            "handshake",
            "heartbeat",
            "terminal",
            "user",
            "broker",
            "server",
            "account",
            "financial",
            "symbols",
            "prices",
            "orders",
            "executions",
            "deals",
            "trades",
            "positions",
            "history",
            "activity",
        }
    )

    def __init__(
        self,
        *,
        login: int | str | None = None,
        password: str | None = None,
        server: str | None = None,
        path: str | None = None,
        endpoint: str | None = None,
        environment: str = "development",
        pairing_token: str | None = None,
        timeout: float = 18.0,
    ) -> None:
        """
        Construct the MT4 bridge.

        Parameters
        ----------
        login:
            MT4 account/login identifier.

        password:
            Retained for connection-layer compatibility.

            The bridge deliberately does NOT transmit the broker
            password as part of evidence requests.

        server:
            MT4 broker/server identity expected by the connection.

        path:
            MT4 terminal executable/path, where applicable.

        endpoint:
            Optional explicit bridge endpoint.

        environment:
            "development" / "local" or
            "production" / "live".

        pairing_token:
            TTL bridge pairing/session credential.

        timeout:
            HTTP request timeout in seconds.
        """

        self.login_id = (
            str(login)
            if login not in (None, "")
            else None
        )

        self.password = password
        self.server_name = server
        self.path = path

        raw_environment = (
            environment or "development"
        ).strip().lower()

        self.environment = {
            "development": "development",
            "dev": "development",
            "local": "development",
            "demo": "development",
            "sandbox": "development",
            "production": "production",
            "prod": "production",
            "live": "production",
        }.get(
            raw_environment,
            raw_environment,
        )

        self.endpoint = self._resolve_endpoint(
            endpoint
        )

        self.pairing_token = pairing_token
        self.timeout = float(timeout)

        self.session_id: str | None = None

        self._connected = False

        self._terminal_identity: dict[str, Any] = {}

        self._last_heartbeat: datetime | None = None

    # ------------------------------------------------------------------
    # Provider / Bridge Identity
    # ------------------------------------------------------------------

    @property
    def version(self) -> str:
        return self.BRIDGE_VERSION

    @property
    def provider(self) -> str:
        return "MetaTrader 4"

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def terminal_identity(self) -> dict[str, Any]:
        return dict(self._terminal_identity)

    @property
    def last_heartbeat(self) -> datetime | None:
        return self._last_heartbeat

    # ------------------------------------------------------------------
    # Endpoint Configuration
    # ------------------------------------------------------------------

    def _resolve_endpoint(
        self,
        endpoint: str | None,
    ) -> str:
        if endpoint:
            return endpoint.rstrip("/")

        if self.environment in {
            "production",
            "prod",
            "live",
        }:
            production_endpoint = (
                self.DEFAULT_PRODUCTION_ENDPOINT
            )

            if not production_endpoint:
                raise MT4BridgeConnectionError(
                    "MT4 production bridge endpoint is not configured. "
                    "Set MT4_BRIDGE_PRODUCTION_ENDPOINT."
                )

            return production_endpoint.rstrip("/")

        return self.DEFAULT_LOCAL_ENDPOINT.rstrip("/")

    # ------------------------------------------------------------------
    # Protocol Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _request_id() -> str:
        return str(uuid4())

    def _build_request(
        self,
        *,
        operation: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if operation not in self.OPERATIONS:
            raise MT4BridgeProtocolError(
                f"Unsupported MT4 bridge operation: {operation}"
            )

        return {
            "protocol_version": self.PROTOCOL_VERSION,
            "bridge_version": self.BRIDGE_VERSION,
            "role": "client",
            "request_id": self._request_id(),
            "operation": operation,
            "session_id": self.session_id,
            "timestamp": self._utc_now(),
            "payload": payload or {},
        }

    @staticmethod
    def _build_headers(
        *,
        pairing_token: str | None,
    ) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TTL-MT4-Bridge/1.0",
        }

        if pairing_token:
            headers["Authorization"] = (
                f"Bearer {pairing_token}"
            )

        return headers

    # ------------------------------------------------------------------
    # HTTP Transport
    # ------------------------------------------------------------------

    def _post(
        self,
        request_payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = json.dumps(
            request_payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers=self._build_headers(
                pairing_token=self.pairing_token,
            ),
            method="POST",
        )

        context = None

        if self.endpoint.startswith("https://"):
            context = ssl.create_default_context()

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
                context=context,
            ) as response:

                raw = response.read()

        except urllib.error.HTTPError as exc:
            try:
                raw_error = exc.read().decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                raw_error = ""

            raise MT4BridgeConnectionError(
                "MT4 bridge HTTP error "
                f"{exc.code}: {raw_error}"
            ) from exc

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as exc:

            raise MT4BridgeConnectionError(
                "Unable to reach MT4 bridge endpoint "
                f"{self.endpoint}: {exc}"
            ) from exc

        try:
            response_payload = json.loads(
                raw.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:

            raise MT4BridgeProtocolError(
                "MT4 bridge returned invalid JSON."
            ) from exc

        if not isinstance(
            response_payload,
            dict,
        ):
            raise MT4BridgeProtocolError(
                "MT4 bridge response must be a JSON object."
            )

        return response_payload

    # ------------------------------------------------------------------
    # Response Validation
    # ------------------------------------------------------------------

    def _validate_response(
        self,
        *,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> dict[str, Any]:

        request_id = request_payload.get(
            "request_id"
        )

        response_request_id = (
            response_payload.get("request_id")
        )

        if (
            request_id is not None
            and response_request_id != request_id
        ):
            raise MT4BridgeProtocolError(
                "MT4 bridge response request_id does "
                "not match the request."
            )

        protocol_version = (
            response_payload.get(
                "protocol_version"
            )
        )

        if protocol_version != self.PROTOCOL_VERSION:
            raise MT4BridgeProtocolError(
                "Unsupported MT4 bridge protocol version: "
                f"{protocol_version!r}"
            )

        operation = request_payload.get(
            "operation"
        )

        response_operation = (
            response_payload.get("operation")
        )

        if response_operation != operation:
            raise MT4BridgeProtocolError(
                "MT4 bridge response operation does "
                "not match the request."
            )

        ok = response_payload.get("ok")

        if ok is not True:
            error = response_payload.get(
                "error"
            )

            if isinstance(error, dict):
                code = error.get(
                    "code",
                    "MT4_BRIDGE_ERROR",
                )
                message = error.get(
                    "message",
                    "MT4 bridge request failed.",
                )
            else:
                code = "MT4_BRIDGE_ERROR"
                message = (
                    str(error)
                    if error is not None
                    else "MT4 bridge request failed."
                )

            raise MT4BridgeProtocolError(
                f"{code}: {message}"
            )

        return response_payload

    # ------------------------------------------------------------------
    # Generic Request
    # ------------------------------------------------------------------

    def request(
        self,
        operation: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute one MT4 bridge operation.

        This method performs no canonical evidence mapping.
        It only handles bridge transport and protocol validation.
        """

        request_payload = self._build_request(
            operation=operation,
            payload=payload,
        )

        response_payload = self._post(
            request_payload
        )

        validated = self._validate_response(
            request_payload=request_payload,
            response_payload=response_payload,
        )

        return validated.get("data")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Establish the logical MT4 bridge session.

        The MT4 terminal itself remains responsible for its
        broker authentication.
        """

        handshake_payload = {
            "account": self.login_id,
            "server": self.server_name,
            "terminal_path": self.path,
            "environment": self.environment,
            "bridge_version": self.BRIDGE_VERSION,
        }

        data = self.request(
            "handshake",
            handshake_payload,
        )

        if data is not None and not isinstance(
            data,
            dict,
        ):
            raise MT4BridgeProtocolError(
                "MT4 handshake data must be an object."
            )

        data = data or {}

        session_id = data.get(
            "session_id"
        )

        if not session_id:
            raise MT4BridgeProtocolError(
                "MT4 bridge handshake did not "
                "return a session_id."
            )

        self.session_id = str(
            session_id
        )

        self._terminal_identity = dict(
            data
        )

        self._connected = True

        self._last_heartbeat = (
            datetime.now(UTC)
        )

    def disconnect(self) -> None:
        """
        Terminate the logical bridge session.

        A remote disconnect operation is optional in the
        protocol. Local session state is always cleared.
        """

        if self.session_id:
            try:
                self.request(
                    "heartbeat",
                    {
                        "state": "disconnecting",
                    },
                )
            except MT4BridgeError:
                # Local teardown should not mask the original
                # disconnect request.
                pass

        self.session_id = None
        self._connected = False
        self._terminal_identity = {}
        self._last_heartbeat = None

    def is_connected(self) -> bool:
        return self._connected

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    def heartbeat(self) -> dict[str, Any]:
        if not self._connected:
            raise MT4BridgeConnectionError(
                "MT4 bridge is not connected."
            )

        data = self.request(
            "heartbeat",
            {
                "account": self.login_id,
                "server": self.server_name,
                "environment": self.environment,
            },
        )

        self._last_heartbeat = (
            datetime.now(UTC)
        )

        if isinstance(data, dict):
            return data

        return {}

    # ------------------------------------------------------------------
    # Provider Evidence Operations
    #
    # These methods intentionally return raw bridge data.
    # MT4Adapter owns canonicalization.
    # ------------------------------------------------------------------

    def terminal(self) -> Any:
        return self.request("terminal")

    def user(self) -> Any:
        return self.request("user")

    def broker(self) -> Any:
        return self.request("broker")

    def server(self) -> Any:
        return self.request("server")

    def account(self) -> Any:
        return self.request("account")

    def financial(self) -> Any:
        return self.request("financial")

    def symbols(self) -> Any:
        return self.request("symbols")

    def prices(self) -> Any:
        return self.request("prices")

    def orders(self) -> Any:
        return self.request("orders")

    def executions(self) -> Any:
        return self.request("executions")

    def deals(self) -> Any:
        return self.request("deals")

    def trades(self) -> Any:
        return self.request("trades")

    def positions(self) -> Any:
        return self.request("positions")

    def history(self) -> Any:
        return self.request("history")

    def activity(self) -> Any:
        return self.request("activity")