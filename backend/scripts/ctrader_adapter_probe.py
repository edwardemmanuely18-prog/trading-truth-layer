from __future__ import annotations

import os
import sys

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.evidence_acquisition.desktop_trading_engine.adapters.ctrader_adapter import (
    CTraderAdapter,
)


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value.strip()


def main() -> int:
    credentials = {
        "client_id": env("CTRADER_CLIENT_ID"),
        "client_secret": env("CTRADER_CLIENT_SECRET"),
        "access_token": env("CTRADER_ACCESS_TOKEN"),
        "account_id": "48298956",
    }

    adapter = None

    print("=" * 80)
    print("TRADING TRUTH LAYER — cTrader ADAPTER PROBE")
    print("=" * 80)
    print("environment: demo")
    print("account_id: 48298956")
    print("=" * 80)

    try:
        print("\n[1] CONSTRUCT")
        adapter = CTraderAdapter.from_connection_config(
            credentials=credentials,
            environment="demo",
        )
        print("CONSTRUCTION: PASS")

        print("\n[2] CONNECT")
        adapter.connect()
        print("CONNECT: PASS")

        print("\n[3] CONNECTION STATE")
        connected = adapter.is_connected()
        print("IS_CONNECTED:", connected)

        if not connected:
            raise RuntimeError(
                "Adapter.connect() returned but is_connected() is False."
            )

        print("\n[4] VERIFICATION SNAPSHOT")
        verification = adapter.get_verification_snapshot()

        print(
            {
                "provider": verification.provider,
                "provider_version": verification.provider_version,
                "connected": verification.connected,
                "account_id": verification.account_id,
                "broker": verification.broker,
                "server": verification.server,
                "terminal": verification.terminal,
                "terminal_version": verification.terminal_version,
                "metadata": verification.metadata,
            }
        )

        print("VERIFICATION: PASS")

        print("\n[5] ACQUIRE")
        payload = adapter.acquire()

        print("ACQUIRE: PASS")
        print("PAYLOAD_TYPE:", type(payload).__name__)

        if isinstance(payload, dict):
            print("\n=== CANONICAL PAYLOAD ===")

            print("connector_name:", payload.get("connector_name"))
            print("connector_version:", payload.get("connector_version"))
            print("schema_version:", payload.get("schema_version"))

            account = payload.get("account")
            financial = payload.get("financial")
            symbols = payload.get("symbols")
            prices = payload.get("prices")
            orders = payload.get("orders")
            executions = payload.get("executions")
            deals = payload.get("deals")
            trades = payload.get("trades")
            positions = payload.get("positions")
            history = payload.get("history")
            activity = payload.get("activity")

            print("account:", type(account).__name__)
            print("financial:", type(financial).__name__)

            print("symbols:", len(symbols or []))
            print("prices:", len(prices or []))
            print("orders:", len(orders or []))
            print("executions:", len(executions or []))
            print("deals:", len(deals or []))
            print("trades:", len(trades or []))
            print("positions:", len(positions or []))
            print("history:", len(history or []))
            print("activity:", len(activity or []))

        print("\n" + "=" * 80)
        print("CTRADER ADAPTER PROBE: PASS")
        print("=" * 80)

        return 0

    except Exception as exc:
        print("\n" + "=" * 80)
        print("CTRADER ADAPTER PROBE: FAILED")
        print("=" * 80)
        print(f"{type(exc).__name__}: {exc}")
        return 1

    finally:
        if adapter is not None:
            try:
                print("\n[6] DISCONNECT")
                adapter.disconnect()
                print("DISCONNECT: PASS")
            except Exception as exc:
                print(
                    "DISCONNECT: WARNING — "
                    f"{type(exc).__name__}: {exc}"
                )


if __name__ == "__main__":
    raise SystemExit(main())