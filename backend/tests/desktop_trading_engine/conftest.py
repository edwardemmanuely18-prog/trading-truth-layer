"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Engine

Shared pytest fixtures for all Desktop Trading Engine tests.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT
TEST_ROOT = Path(__file__).resolve().parent

ENV_FILE = PROJECT_ROOT / ".env.testing"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError(
        f"Testing environment file not found: {ENV_FILE}"
    )

# ============================================================
# Helper Functions
# ============================================================


def _required_env(name: str) -> str:
    """
    Return a required environment variable.

    Fails the test session immediately if missing.
    """

    value = os.getenv(name)

    if value is None or value.strip() == "":
        pytest.fail(
            f"Required environment variable '{name}' "
            f"is missing from .env.testing"
        )

    return value.strip()


def _optional_env(name: str, default: str) -> str:
    """
    Return an optional environment variable.
    """

    return os.getenv(name, default).strip()


# ============================================================
# Project Fixtures
# ============================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def backend_root() -> Path:
    return BACKEND_ROOT


@pytest.fixture(scope="session")
def test_root() -> Path:
    return TEST_ROOT


# ============================================================
# MT5 Configuration
# ============================================================


@pytest.fixture(scope="session")
def mt5_terminal() -> str:

    terminal = _required_env("MT5_TERMINAL")

    if not Path(terminal).exists():
        pytest.fail(
            f"MT5 terminal executable not found:\n{terminal}"
        )

    return terminal


@pytest.fixture(scope="session")
def mt5_login() -> int:
    return int(_required_env("MT5_LOGIN"))


@pytest.fixture(scope="session")
def mt5_password() -> str:
    return _required_env("MT5_PASSWORD")


@pytest.fixture(scope="session")
def mt5_server() -> str:
    return _required_env("MT5_SERVER")


# ============================================================
# Interactive Brokers Configuration
# ============================================================


@pytest.fixture(scope="session")
def ibkr_host() -> str:
    return _optional_env("IBKR_HOST", "127.0.0.1")


@pytest.fixture(scope="session")
def ibkr_port() -> int:
    return int(_optional_env("IBKR_PORT", "7497"))


@pytest.fixture(scope="session")
def ibkr_client_id() -> int:
    return int(_optional_env("IBKR_CLIENT_ID", "1"))


# ============================================================
# Synchronization Configuration
# ============================================================


@pytest.fixture(scope="session")
def synchronization_timeout() -> int:
    return int(_optional_env("SYNC_TIMEOUT", "60"))


@pytest.fixture(scope="session")
def synchronization_batch_size() -> int:
    return int(_optional_env("SYNC_BATCH_SIZE", "1000"))


# ============================================================
# Evidence Configuration
# ============================================================


@pytest.fixture(scope="session")
def enable_history_download() -> bool:
    return (
        _optional_env("DOWNLOAD_HISTORY", "true").lower()
        == "true"
    )


@pytest.fixture(scope="session")
def enable_position_download() -> bool:
    return (
        _optional_env("DOWNLOAD_POSITIONS", "true").lower()
        == "true"
    )


@pytest.fixture(scope="session")
def enable_order_download() -> bool:
    return (
        _optional_env("DOWNLOAD_ORDERS", "true").lower()
        == "true"
    )


# ============================================================
# Test Metadata
# ============================================================


@pytest.fixture(scope="session")
def test_environment() -> dict:

    return {
        "project_root": PROJECT_ROOT,
        "backend_root": BACKEND_ROOT,
        "test_root": TEST_ROOT,
        "mt5_terminal": os.getenv("MT5_TERMINAL"),
        "mt5_server": os.getenv("MT5_SERVER"),
        "ibkr_host": os.getenv("IBKR_HOST", "127.0.0.1"),
        "ibkr_port": int(os.getenv("IBKR_PORT", "7497")),
        "timeout": int(os.getenv("SYNC_TIMEOUT", "60")),
        "batch_size": int(os.getenv("SYNC_BATCH_SIZE", "1000")),
    }