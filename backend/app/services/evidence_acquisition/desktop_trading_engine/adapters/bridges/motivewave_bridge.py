"""
Trading Truth Layer
MotiveWave Desktop Bridge

Thin transport/session layer.

This client intentionally does NOT:
    - normalize evidence
    - canonicalize evidence
    - verify evidence
    - synchronize evidence
    - implement business logic

Those responsibilities remain in MotiveWaveAdapter
and the shared Desktop Trading Engine.
"""

from __future__ import annotations

import json
import os
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class MotiveWaveBridgeError(RuntimeError):
    """Base MotiveWave bridge error."""


class MotiveWaveBridgeConnectionError(
    MotiveWaveBridgeError
):
    """Raised when the MotiveWave bridge cannot be reached."""


class MotiveWaveBridgeProtocolError(
    MotiveWaveBridgeError
):
    """Raised when the MotiveWave bridge violates the protocol."""


# ============================================================================
# Server-side MotiveWave rendezvous state
# ============================================================================

_MOTIVEWAVE_BRIDGE_WAIT_SECONDS = float(
    os.getenv(
        "MOTIVEWAVE_BRIDGE_WAIT_SECONDS",
        "30",
    )
)

_MOTIVEWAVE_SESSION_TTL_SECONDS = float(
    os.getenv(
        "MOTIVEWAVE_SESSION_TTL_SECONDS",
        "120",
    )
)


@dataclass
class _PendingMotiveWaveRequest:
    request: dict[str, Any]
    response: dict[str, Any] | None = None
    event: threading.Event = field(
        default_factory=threading.Event
    )


@dataclass
class _MotiveWaveSession:
    session_id: str
    connected: bool = False
    last_seen: float = field(
        default_factory=time.time
    )

    terminal: dict[str, Any] = field(
        default_factory=dict
    )

    account: str | None = None
    account_name: str | None = None
    environment: str = "development"

    pending: dict[
        str,
        _PendingMotiveWaveRequest,
    ] = field(
        default_factory=dict
    )


_MOTIVEWAVE_SESSIONS: dict[
    str,
    _MotiveWaveSession,
] = {}

_MOTIVEWAVE_SESSIONS_LOCK = (
    threading.RLock()
)

def _motivewave_success(
    *,
    request_id: str,
    operation: str,
    data: Any = None,
) -> dict[str, Any]:
    return {
        "protocol_version": (
            MotiveWaveBridge.PROTOCOL_VERSION
        ),
        "request_id": request_id,
        "operation": operation,
        "ok": True,
        "data": data,
        "error": None,
    }


def _motivewave_error(
    *,
    request_id: str,
    operation: str,
    code: str,
    message: str,
) -> dict[str, Any]:
    return {
        "protocol_version": (
            MotiveWaveBridge.PROTOCOL_VERSION
        ),
        "request_id": request_id,
        "operation": operation,
        "ok": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _find_motivewave_session(
    *,
    session_id: str | None = None,
    account: str | None = None,
    environment: str | None = None,
) -> _MotiveWaveSession | None:

    with _MOTIVEWAVE_SESSIONS_LOCK:

        if session_id:
            session = _MOTIVEWAVE_SESSIONS.get(
                str(session_id)
            )

            if session is not None:
                return session

        normalized_environment = (
            environment or ""
        ).strip().lower()

        for session in (
            _MOTIVEWAVE_SESSIONS.values()
        ):
            if not session.connected:
                continue

            if account is not None:
                if session.account != str(account):
                    continue

            if normalized_environment:
                if (
                    session.environment
                    != normalized_environment
                ):
                    continue

            return session

    return None


def _register_motivewave_terminal(
    *,
    request_id: str,
    session_id: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:

    resolved_session_id = (
        str(session_id)
        if session_id
        else str(uuid4())
    )

    account = payload.get(
        "account"
    )

    account_name = payload.get(
        "account_name"
    )

    environment = (
        payload.get(
            "environment"
        )
        or "development"
    ).strip().lower()

    with _MOTIVEWAVE_SESSIONS_LOCK:

        session = _MOTIVEWAVE_SESSIONS.get(
            resolved_session_id
        )

        if session is None:

            session = _MotiveWaveSession(
                session_id=resolved_session_id
            )

            _MOTIVEWAVE_SESSIONS[
                resolved_session_id
            ] = session

        session.connected = True
        session.last_seen = time.time()

        if account is not None:
            session.account = str(account)

        if account_name is not None:
            session.account_name = str(
                account_name
            )

        session.environment = (
            environment
        )

        session.terminal = {
            "provider": payload.get(
                "provider",
                "MotiveWave",
            ),
            "bridge_version": payload.get(
                "bridge_version"
            ),
            "java_version": payload.get(
                "java_version"
            ),
            "os_name": payload.get(
                "os_name"
            ),
            "os_arch": payload.get(
                "os_arch"
            ),
        }

    return _motivewave_success(
        request_id=request_id,
        operation="heartbeat",
        data={
            "session_id": (
                resolved_session_id
            ),
            "account": session.account,
            "account_name": (
                session.account_name
            ),
            "environment": (
                session.environment
            ),
            "terminal": session.terminal,
        },
    )


def _poll_motivewave_terminal(
    *,
    request_id: str,
    session_id: str | None,
) -> dict[str, Any]:

    session = _find_motivewave_session(
        session_id=session_id
    )

    if session is None:
        return _motivewave_error(
            request_id=request_id,
            operation="poll",
            code="MOTIVEWAVE_SESSION_NOT_FOUND",
            message=(
                "MotiveWave bridge session was "
                "not found or is no longer active."
            ),
        )

    with _MOTIVEWAVE_SESSIONS_LOCK:

        session.last_seen = time.time()

        pending = next(
            iter(
                session.pending.values()
            ),
            None,
        )

        if pending is None:
            return _motivewave_success(
                request_id=request_id,
                operation="poll",
                data=None,
            )

        return _motivewave_success(
            request_id=request_id,
            operation="poll",
            data=pending.request,
        )


def _receive_motivewave_response(
    *,
    request_id: str,
    session_id: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:

    session = _find_motivewave_session(
        session_id=session_id
    )

    if session is None:
        return _motivewave_error(
            request_id=request_id,
            operation="response",
            code="MOTIVEWAVE_SESSION_NOT_FOUND",
            message=(
                "MotiveWave bridge session "
                "was not found."
            ),
        )

    response_request_id = payload.get(
        "request_id"
    )

    if not response_request_id:
        return _motivewave_error(
            request_id=request_id,
            operation="response",
            code="MOTIVEWAVE_REQUEST_ID_MISSING",
            message=(
                "MotiveWave response request_id "
                "is missing."
            ),
        )

    with _MOTIVEWAVE_SESSIONS_LOCK:

        pending = session.pending.get(
            str(response_request_id)
        )

        if pending is None:
            return _motivewave_error(
                request_id=request_id,
                operation="response",
                code=(
                    "MOTIVEWAVE_PENDING_REQUEST_NOT_FOUND"
                ),
                message=(
                    "No pending MotiveWave request "
                    f"exists for {response_request_id}."
                ),
            )

        pending.response = payload
        pending.event.set()

    return _motivewave_success(
        request_id=request_id,
        operation="response",
        data={
            "accepted": True,
            "request_id": (
                response_request_id
            ),
        },
    )


def _dispatch_motivewave_request(
    *,
    message: dict[str, Any],
    session_id: str | None,
    account: str | None,
    environment: str,
) -> dict[str, Any]:

    session = _find_motivewave_session(
        session_id=session_id,
        account=account,
        environment=environment,
    )

    if session is None:
        return _motivewave_error(
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
            code=(
                "MOTIVEWAVE_TERMINAL_NOT_CONNECTED"
            ),
            message=(
                "No active MotiveWave terminal "
                "bridge session matches the "
                "requested account/environment."
            ),
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

    pending = _PendingMotiveWaveRequest(
        request=message
    )

    with _MOTIVEWAVE_SESSIONS_LOCK:

        session.pending[
            request_id
        ] = pending

        session.last_seen = time.time()

    completed = pending.event.wait(
        timeout=(
            _MOTIVEWAVE_BRIDGE_WAIT_SECONDS
        )
    )

    with _MOTIVEWAVE_SESSIONS_LOCK:

        session.pending.pop(
            request_id,
            None,
        )

    if not completed:
        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_TERMINAL_RESPONSE_TIMEOUT"
            ),
            message=(
                "The MotiveWave terminal did "
                "not respond within the bridge "
                "timeout."
            ),
        )

    response = pending.response

    if not isinstance(
        response,
        dict,
    ):
        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_TERMINAL_RESPONSE_INVALID"
            ),
            message=(
                "The MotiveWave terminal returned "
                "an invalid response."
            ),
        )

    response_operation = response.get(
        "operation"
    )

    if response_operation != operation:
        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_OPERATION_MISMATCH"
            ),
            message=(
                "MotiveWave terminal response "
                "operation does not match the "
                "requested operation."
            ),
        )

    return {
        "protocol_version": (
            MotiveWaveBridge.PROTOCOL_VERSION
        ),
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


def handle_motivewave_bridge_message(
    message: dict[str, Any],
    *,
    authorization: str | None = None,
) -> dict[str, Any]:
    """
    Server-side MotiveWave bridge rendezvous handler.

    Transport/session mechanics only.

    This function does not:
        - acquire evidence
        - normalize evidence
        - canonicalize evidence
        - verify evidence
        - synchronize evidence
        - make business decisions
    """

    configured_token = os.getenv(
        "MOTIVEWAVE_BRIDGE_TOKEN",
        "",
    ).strip()

    if configured_token:

        expected = (
            f"Bearer {configured_token}"
        )

        if authorization != expected:
            return _motivewave_error(
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
                code=(
                    "MOTIVEWAVE_BRIDGE_UNAUTHORIZED"
                ),
                message=(
                    "Invalid MotiveWave bridge "
                    "authorization."
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

    payload = (
        message.get(
            "payload"
        )
        or {}
    )

    if protocol_version != (
        MotiveWaveBridge.PROTOCOL_VERSION
    ):
        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_PROTOCOL_VERSION_UNSUPPORTED"
            ),
            message=(
                "Unsupported MotiveWave protocol "
                f"version: {protocol_version!r}"
            ),
        )

    if not isinstance(
        payload,
        dict,
    ):
        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_PAYLOAD_INVALID"
            ),
            message=(
                "MotiveWave bridge payload "
                "must be a JSON object."
            ),
        )

        if operation == "debug_state":

            with _MOTIVEWAVE_SESSIONS_LOCK:

                sessions = {}

                for sid, session in (
                    _MOTIVEWAVE_SESSIONS.items()
                ):
                    sessions[str(sid)] = {
                        "session_id": session.session_id,
                        "connected": session.connected,
                        "account": session.account,
                        "account_name": session.account_name,
                        "environment": session.environment,
                        "pending_count": len(
                            session.pending
                        ),
                        "pending_request_ids": list(
                            session.pending.keys()
                        ),
                        "last_seen": session.last_seen,
                    }

        return _motivewave_success(
            request_id=request_id,
            operation="debug_state",
            data={
                "process_id": os.getpid(),
                "sessions": sessions,
            },
        )

    # ------------------------------------------------------------------
    # Terminal → backend
    # ------------------------------------------------------------------

    if role == "terminal":

        if operation == "heartbeat":

            return _register_motivewave_terminal(
                request_id=request_id,
                session_id=(
                    str(session_id)
                    if session_id
                    else None
                ),
                payload=payload,
            )

        if operation == "poll":

            return _poll_motivewave_terminal(
                request_id=request_id,
                session_id=(
                    str(session_id)
                    if session_id
                    else None
                ),
            )

        if operation == "response":

            return _receive_motivewave_response(
                request_id=request_id,
                session_id=(
                    str(session_id)
                    if session_id
                    else None
                ),
                payload=payload,
            )

        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_TERMINAL_OPERATION_UNSUPPORTED"
            ),
            message=(
                f"Unsupported terminal operation: "
                f"{operation}"
            ),
        )

    # ------------------------------------------------------------------
    # Backend/client → terminal
    # ------------------------------------------------------------------

    if role != "client":

        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_BRIDGE_ROLE_INVALID"
            ),
            message=(
                "Bridge message role must be "
                "'client' or 'terminal'."
            ),
        )

    if operation not in (
        MotiveWaveBridge.OPERATIONS
    ):
        return _motivewave_error(
            request_id=request_id,
            operation=operation,
            code=(
                "MOTIVEWAVE_OPERATION_UNSUPPORTED"
            ),
            message=(
                f"Unsupported MotiveWave operation: "
                f"{operation}"
            ),
        )

    account = payload.get(
        "account"
    )

    environment = (
        payload.get(
            "environment"
        )
        or "development"
    ).strip().lower()

    return _dispatch_motivewave_request(
        message=message,
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
        environment=environment,
    )


class MotiveWaveBridge:

    PROTOCOL_VERSION = "1.0"
    BRIDGE_VERSION = "1.1"

    DEFAULT_LOCAL_ENDPOINT = (
        "http://127.0.0.1:17841"
    )

    DEFAULT_PRODUCTION_ENDPOINT = os.getenv(
        "MOTIVEWAVE_BRIDGE_PRODUCTION_ENDPOINT",
        "https://www.tradingtruthlayer.com/api/evidence-acquisition/motivewave-bridge",
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

    TERMINAL_OPERATIONS = frozenset(
        {
            "poll",
            "response",
        }
    )

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        environment: str = "development",
        pairing_token: str | None = None,
        timeout: float = 15.0,
        account_id: str | None = None,
        account_name: str | None = None,
        account_environment: str = "development",
    ) -> None:

        self.environment = (
            environment or "development"
        ).strip().lower()

        self.endpoint = (
            endpoint
            or (
                self.DEFAULT_PRODUCTION_ENDPOINT
                if self.environment
                in {
                    "production",
                    "prod",
                    "live",
                }
                and self.DEFAULT_PRODUCTION_ENDPOINT
                else self.DEFAULT_LOCAL_ENDPOINT
            )
        ).rstrip("/")

        self.pairing_token = pairing_token
        self.timeout = float(timeout)

        self.account_id = (
            str(account_id)
            if account_id not in (
                None,
                "",
            )
            else None
        )

        self.account_name = (
            str(account_name)
            if account_name not in (
                None,
                "",
            )
            else None
        )

        self.account_environment = (
            account_environment
            or "development"
        ).strip().lower()

        self.session_id: str | None = None
        self._connected = False
        self._terminal_identity: dict[str, Any] = {}
        self._last_heartbeat: datetime | None = None

    @property
    def version(self) -> str:
        value = self._terminal_identity.get(
            "bridge_version"
        )
        return str(
            value
            or self.BRIDGE_VERSION
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:

        data = self.request(
            "handshake"
        )

        if not isinstance(
            data,
            dict,
        ):
            raise MotiveWaveBridgeProtocolError(
                "MotiveWave handshake data must be an object."
            )

        session_id = data.get(
            "session_id"
        )

        if not session_id:
            raise MotiveWaveBridgeProtocolError(
                "MotiveWave bridge handshake did not "
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

        self.session_id = None
        self._connected = False
        self._terminal_identity = {}
        self._last_heartbeat = None

    def is_connected(self) -> bool:

        if not self._connected:
            return False

        try:
            data = self.request(
                "heartbeat"
            )

            return (
                isinstance(data, dict)
                and data.get("state")
                == "active"
            )

        except MotiveWaveBridgeError:
            self._connected = False
            return False

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    def heartbeat(self) -> dict[str, Any]:

        if not self._connected:
            raise MotiveWaveBridgeConnectionError(
                "MotiveWave bridge is not connected."
            )

        data = self.request(
            "heartbeat"
        )

        self._last_heartbeat = (
            datetime.now(UTC)
        )

        return (
            data
            if isinstance(data, dict)
            else {}
        )

    # ------------------------------------------------------------------
    # Provider operations
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
        """
        Return provider-native account evidence.

        MotiveWave's OrderContext may expose financial/account state while
        leaving account_id null. When that happens, resolve the account
        identity from provider-native execution/position evidence rather than
        substituting TTL configuration blindly.

        This remains provider transport logic only. No canonical
        verification
        or business decision is performed here.
        """
        account_data = self.request("account")

        if not isinstance(account_data, dict):
            return account_data

        # Native account metadata is authoritative when available.
        account_id = account_data.get("account_id")
        if account_id not in (None, ""):
            return account_data

        # --------------------------------------------------------------
        # Provider-native identity fallback
        # --------------------------------------------------------------
        #
        # The current MotiveWave OrderContext does not expose a canonical
        # account identifier through the account metadata surface. However,
        # execution/position records can expose the native account id.
        #
        for operation in (
            "positions",
            "executions",
            "trades",
        ):
            try:
                records = self.request(operation)
            except MotiveWaveBridgeError:
                continue

            if not isinstance(records, list):
                continue

            for record in records:
                if not isinstance(record, dict):
                    continue

                native_account_id = record.get("account_id")

                if native_account_id not in (None, ""):
                    resolved = dict(account_data)

                    resolved["account_id"] = str(
                        native_account_id
                    )

                    resolved["account_identity_source"] = (
                        f"MotiveWave {operation}"
                    )

                    resolved["account_identity_confidence"] = (
                        "provider_native"
                    )

                    return resolved

        # Preserve the original provider-native response when no native
        # account identity is currently exposed.
        return account_data

    def account_identity(self) -> dict[str, Any]:
        """
        Resolve the provider-native MotiveWave account identity
        without changing verification state.
        """
        account_data = self.account()

        if not isinstance(account_data, dict):
            return {
                "account_id": None,
                "account_identity_source": None,
                "account_identity_confidence": "unavailable",
            }

        return {
            "account_id": account_data.get("account_id"),
            "account_identity_source": account_data.get(
                "account_identity_source"
            ),
            "account_identity_confidence": account_data.get(
                "account_identity_confidence"
            ),
        }

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

    # ------------------------------------------------------------------
    # Protocol
    # ------------------------------------------------------------------

    @staticmethod
    def _request_id() -> str:
        return str(uuid4())

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()

    def _build_url(
        self,
        operation: str,
    ) -> str:

        if operation not in self.OPERATIONS:
            raise MotiveWaveBridgeProtocolError(
                f"Unsupported MotiveWave bridge operation: "
                f"{operation}"
            )

        request_id = self._request_id()

        params = {
            "request_id": request_id,
        }

        if self.session_id:
            params["session_id"] = (
                self.session_id
            )

        query = urllib.parse.urlencode(
            params
        )

        return (
            f"{self.endpoint}/v1/"
            f"{operation}?{query}"
        ), request_id

    def _headers(self) -> dict[str, str]:

        headers = {
            "Accept": "application/json",
            "User-Agent":
                "TTL-MotiveWave-Bridge/1.1",
        }

        if self.pairing_token:
            headers["Authorization"] = (
                f"Bearer {self.pairing_token}"
            )

        return headers

    def _post_rendezvous(
        self,
        operation: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], str]:

        request_id = self._request_id()

        message = {
            "protocol_version": (
                self.PROTOCOL_VERSION
            ),
            "request_id": request_id,
            "operation": operation,
            "role": "client",
            "session_id": self.session_id,
            "payload": {
                **(
                    payload
                    if payload is not None
                    else {}
                ),
                "account": self.account_id,
                "account_name": self.account_name,
                "environment": (
                    self.account_environment
                ),
            },
        }

        body = json.dumps(
            message
        ).encode("utf-8")

        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                **self._headers(),
                "Content-Type": (
                    "application/json"
                ),
            },
            method="POST",
        )

        context = None

        if self.endpoint.startswith(
            "https://"
        ):
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
                raw_error = (
                    exc.read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
                )
            except Exception:
                raw_error = ""

            raise MotiveWaveBridgeConnectionError(
                "MotiveWave rendezvous HTTP error "
                f"{exc.code}: {raw_error}"
            ) from exc

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as exc:

            raise MotiveWaveBridgeConnectionError(
                "Unable to reach MotiveWave rendezvous "
                f"endpoint {self.endpoint}: {exc}"
            ) from exc

        try:

            response_payload = json.loads(
                raw.decode("utf-8")
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:

            raise MotiveWaveBridgeProtocolError(
                "MotiveWave rendezvous returned "
                "invalid JSON."
            ) from exc

        if not isinstance(
            response_payload,
            dict,
        ):
            raise MotiveWaveBridgeProtocolError(
                "MotiveWave rendezvous response "
                "must be a JSON object."
            )

        return response_payload, request_id

    def _get(
        self,
        operation: str,
    ) -> tuple[dict[str, Any], str]:

        url, request_id = (
            self._build_url(operation)
        )

        request = urllib.request.Request(
            url,
            headers=self._headers(),
            method="GET",
        )

        context = None

        if self.endpoint.startswith(
            "https://"
        ):
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
                raw_error = (
                    exc.read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
                )
            except Exception:
                raw_error = ""

            raise MotiveWaveBridgeConnectionError(
                "MotiveWave bridge HTTP error "
                f"{exc.code}: {raw_error}"
            ) from exc

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as exc:

            raise MotiveWaveBridgeConnectionError(
                "Unable to reach MotiveWave bridge "
                f"endpoint {self.endpoint}: {exc}"
            ) from exc

        try:

            payload = json.loads(
                raw.decode("utf-8")
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:

            raise MotiveWaveBridgeProtocolError(
                "MotiveWave bridge returned invalid JSON."
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise MotiveWaveBridgeProtocolError(
                "MotiveWave bridge response must "
                "be a JSON object."
            )

        return payload, request_id

    def _validate_response(
        self,
        *,
        operation: str,
        request_id: str,
        response: dict[str, Any],
    ) -> dict[str, Any]:

        if response.get(
            "request_id"
        ) != request_id:

            raise MotiveWaveBridgeProtocolError(
                "MotiveWave bridge response request_id "
                "does not match the request."
            )

        if response.get(
            "protocol_version"
        ) != self.PROTOCOL_VERSION:

            raise MotiveWaveBridgeProtocolError(
                "Unsupported MotiveWave bridge protocol "
                f"version: {response.get('protocol_version')!r}"
            )

        if response.get(
            "operation"
        ) != operation:

            raise MotiveWaveBridgeProtocolError(
                "MotiveWave bridge response operation "
                "does not match the request."
            )

        if response.get(
            "ok"
        ) is not True:

            error = response.get(
                "error"
            )

            if isinstance(
                error,
                dict,
            ):

                code = error.get(
                    "code",
                    "MOTIVEWAVE_BRIDGE_ERROR",
                )

                message = error.get(
                    "message",
                    "MotiveWave bridge request failed.",
                )

            else:

                code = (
                    "MOTIVEWAVE_BRIDGE_ERROR"
                )

                message = (
                    str(error)
                    if error is not None
                    else "MotiveWave bridge request failed."
                )

            raise MotiveWaveBridgeProtocolError(
                f"{code}: {message}"
            )

        return response

    def request(
        self,
        operation: str,
    ) -> Any:

        if self.environment in {
            "production",
            "prod",
            "live",
        }:
            response, request_id = (
                self._post_rendezvous(
                    operation
                )
            )

        else:
            response, request_id = (
                self._get(
                    operation
                )
            )

        validated = (
            self._validate_response(
                operation=operation,
                request_id=request_id,
                response=response,
            )
        )

        return validated.get(
            "data"
        )