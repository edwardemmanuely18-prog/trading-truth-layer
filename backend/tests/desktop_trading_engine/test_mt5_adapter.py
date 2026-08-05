"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

MT5 Adapter Integration Tests

These tests verify that the MT5 adapter can communicate
with a MetaTrader 5 terminal and acquire evidence.

No trading operations are performed.
"""

from __future__ import annotations

import pytest

pytest.importorskip("MetaTrader5")

import MetaTrader5 as mt5


pytestmark = pytest.mark.integration


# ============================================================
# Connection
# ============================================================

def test_mt5_initialize(mt5_terminal):

    assert mt5.initialize(path=mt5_terminal), (
        f"MT5 initialize failed: {mt5.last_error()}"
    )


def test_mt5_login(
    mt5_login,
    mt5_password,
    mt5_server,
):

    assert mt5.login(
        login=mt5_login,
        password=mt5_password,
        server=mt5_server,
    ), mt5.last_error()


# ============================================================
# Terminal
# ============================================================

def test_terminal_info():

    info = mt5.terminal_info()

    assert info is not None

    print(info)


# ============================================================
# Version
# ============================================================

def test_version():

    version = mt5.version()

    assert version is not None

    print(version)


# ============================================================
# Account
# ============================================================

def test_account_info():

    account = mt5.account_info()

    assert account is not None

    assert account.login > 0

    print(account)


# ============================================================
# Symbols
# ============================================================

def test_symbols():

    symbols = mt5.symbols_get()

    assert symbols is not None

    assert len(symbols) > 0

    print(f"Symbols: {len(symbols)}")


# ============================================================
# Open Positions
# ============================================================

def test_positions():

    positions = mt5.positions_get()

    assert positions is not None

    print(f"Positions: {len(positions)}")


# ============================================================
# Orders
# ============================================================

def test_orders():

    orders = mt5.orders_get()

    assert orders is not None

    print(f"Orders: {len(orders)}")


# ============================================================
# History
# ============================================================

from datetime import datetime, timedelta

# ============================================================
# History
# ============================================================

def test_history():

    utc_to = datetime.now()

    utc_from = utc_to - timedelta(days=365)

    history = mt5.history_deals_get(
        utc_from,
        utc_to,
    )

    if history is None:

        print(f"MT5 Error: {mt5.last_error()}")

        pytest.fail(
            "Unable to retrieve MT5 deal history."
        )

    print(f"History deals: {len(history)}")

    assert isinstance(history, tuple)


# ============================================================
# Shutdown
# ============================================================

def test_shutdown():

    mt5.shutdown()