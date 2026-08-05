"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Engine

Institutional Desktop Diagnostics
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# ============================================================
# Project Paths
# ============================================================

TOOLS_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = TOOLS_DIR.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

ENV_FILE = BACKEND_ROOT / ".env.testing"

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f".env.testing not found:\n{ENV_FILE}"
    )

load_dotenv(ENV_FILE)

# ============================================================
# TTL Imports
# ============================================================

from app.services.evidence_acquisition.desktop_trading_engine.adapters.mt5_adapter import (
    MT5Adapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.ibkr_adapter import (
    IBKRAdapter,
)

# ============================================================
# Command Line
# ============================================================

parser = argparse.ArgumentParser(
    description="Desktop Trading Engine Diagnostics"
)

parser.add_argument(
    "--provider",
    default="mt5",
    choices=[
        "mt5",
        "ibkr",
    ],
    help="Desktop trading provider",
)

args = parser.parse_args()

# ============================================================
# Console Helpers
# ============================================================

LINE = "=" * 70
SECTION = "-" * 28


def banner() -> None:

    print()
    print(LINE)
    print("Trading Truth Layer (TTL)")
    print("Universal Evidence Adapter (UEA)")
    print("Desktop Trading Engine Diagnostics")
    print(LINE)
    print(f"Provider : {args.provider.upper()}")
    print(f"Backend  : {BACKEND_ROOT}")
    print(f"Env File : {ENV_FILE}")
    print(LINE)
    print()


def heading(title: str) -> None:
    print()
    print(title)
    print(SECTION)


def yes_no(value: bool) -> str:
    return "✓" if value else "✗"


def safe_len(value: Any) -> int:
    if value is None:
        return 0

    try:
        return len(value)
    except Exception:
        return 0


# ============================================================
# Diagnostic Report
# ============================================================

@dataclass
class DiagnosticCheck:

    name: str

    passed: bool

    message: str = ""


@dataclass
class DiagnosticReport:

    checks: list[DiagnosticCheck] = field(default_factory=list)

    started_at: float = field(default_factory=time.perf_counter)

    finished_at: float | None = None

    def add(
        self,
        name: str,
        passed: bool,
        message: str = "",
    ) -> None:

        self.checks.append(
            DiagnosticCheck(
                name=name,
                passed=passed,
                message=message,
            )
        )

    @property
    def passed(self) -> bool:

        return all(
            check.passed
            for check in self.checks
        )

    @property
    def failed(self) -> int:

        return len(
            [
                c
                for c in self.checks
                if not c.passed
            ]
        )

    @property
    def succeeded(self) -> int:

        return len(
            [
                c
                for c in self.checks
                if c.passed
            ]
        )

    @property
    def total(self) -> int:

        return len(self.checks)

    @property
    def elapsed(self) -> float:

        end = (
            self.finished_at
            if self.finished_at is not None
            else time.perf_counter()
        )

        return end - self.started_at

    def finish(self) -> None:

        self.finished_at = time.perf_counter()


# ============================================================
# Desktop Diagnostics
# ============================================================

class DesktopDiagnostics:
    """
    Institutional diagnostics for the Desktop Trading Engine.

    Responsibilities
    ----------------

    • Validate environment configuration

    • Validate adapter lifecycle

    • Validate evidence acquisition

    • Display financial summary

    • Display evidence statistics

    • Produce overall PASS / FAIL report
    """

    def __init__(self) -> None:

        self.adapter: MT5Adapter | None = None

        self.payload: dict[str, Any] = {}

        self.report = DiagnosticReport()

        self.connected = False

        self.acquisition_time: float = 0.0

    # --------------------------------------------------------
    # Adapter Factory
    # --------------------------------------------------------

    def build_adapter(self):

        if args.provider == "mt5":

            login = os.getenv("MT5_LOGIN")

            return MT5Adapter(
                login=int(login) if login else None,
                password=os.getenv("MT5_PASSWORD"),
                server=os.getenv("MT5_SERVER"),
                path=os.getenv("MT5_TERMINAL"),
            )

        if args.provider == "ibkr":

            return IBKRAdapter(
                host=os.getenv("IBKR_HOST", "127.0.0.1"),
                port=int(os.getenv("IBKR_PORT", "7497")),
                client_id=int(os.getenv("IBKR_CLIENT_ID", "1")),
            )

        raise RuntimeError(
            f"Unsupported provider: {args.provider}"
        )


    # --------------------------------------------------------
    # Runner
    # --------------------------------------------------------

    def run(self) -> None:

        banner()

        try:

            self.run_environment_checks()

            if not self.report.checks[-1].passed:
                return

            self.run_adapter_lifecycle()

            self.run_evidence_acquisition()

            self.print_financial_summary()

            self.print_statistics()

        finally:

            self.shutdown()

            self.report.finish()

            self.print_summary()

    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    def run_environment_checks(self) -> None:

        heading("Environment")

        if args.provider == "mt5":

            login = os.getenv("MT5_LOGIN")
            password = os.getenv("MT5_PASSWORD")
            server = os.getenv("MT5_SERVER")
            terminal = os.getenv("MT5_TERMINAL")

        elif args.provider == "ibkr":

            login = os.getenv("IBKR_HOST")
            password = os.getenv("IBKR_PORT")
            server = os.getenv("IBKR_CLIENT_ID")
            terminal = None

        else:

            raise RuntimeError(
                f"Unsupported provider: {args.provider}"
            )

        login_ok = bool(login)
        password_ok = bool(password)
        server_ok = bool(server)
        terminal_ok = bool(terminal)

        if args.provider == "mt5":

            print("MT5_LOGIN      :", yes_no(login_ok))
            print("MT5_PASSWORD   :", yes_no(password_ok))
            print("MT5_SERVER     :", yes_no(server_ok))

        else:

            print("IBKR_HOST      :", login)
            print("IBKR_PORT      :", password)
            print("IBKR_CLIENT_ID :", server)

        print(
            "MT5_TERMINAL   :",
            terminal if terminal else "NOT CONFIGURED",
        )

        terminal_exists = False

        if terminal:

            terminal_exists = Path(terminal).exists()

            print(
                "Terminal Path  :",
                "✓ Exists" if terminal_exists else "✗ Missing",
            )

        if args.provider == "mt5":

            environment_ok = (
                login_ok
                and password_ok
                and server_ok
                and terminal_exists
            )

        else:

            environment_ok = (
                login_ok
                and password_ok
                and server_ok
            )

        self.report.add(
            "Environment",
            environment_ok,
        )

    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------

    def run_adapter_lifecycle(self) -> None:

        print()
        print(LINE)
        print("Adapter Lifecycle")
        print(LINE)

        self.adapter = self.build_adapter()

        try:

            self.adapter.connect()

            self.connected = True

            print()

            heading("Provider")

            print(
                "Name     :",
                self.adapter.provider_name,
            )

            print(
                "Version  :",
                self.adapter.provider_version,
            )

            print()

            heading("Connection")

            connected = self.adapter.is_connected()

            print(
                "connect()      : ✓",
            )

            print(
                "is_connected() :",
                yes_no(connected),
            )

            self.report.add(
                "Adapter Lifecycle",
                connected,
            )

        except Exception as exc:

            print()

            print("Connection failed")

            print(exc)

            self.report.add(
                "Adapter Lifecycle",
                False,
                str(exc),
            )

            raise

    # --------------------------------------------------------
    # Evidence Acquisition
    # --------------------------------------------------------

    def run_evidence_acquisition(self) -> None:

        print()
        print(LINE)
        print("Evidence Acquisition")
        print(LINE)

        if not self.adapter:

            raise RuntimeError(
                "Adapter has not been initialized."
            )

        started = time.perf_counter()

        self.payload = self.adapter.acquire()

        self.acquisition_time = (
            time.perf_counter() - started
        )

        print()

        expected_sections = [

            "terminal",

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
        ]

        acquisition_ok = True

        for section in expected_sections:

            value = self.payload.get(section)

            if section in {
                "terminal",
                "account",
                "financial",
            }:
                exists = value is not None
            else:
                exists = section in self.payload

            print(
                f"{section:<14}:",
                yes_no(exists),
            )

            acquisition_ok &= exists

        print()

        print(
            "Acquire Time  :",
            f"{self.acquisition_time:.3f} seconds",
        )

        self.report.add(
            "Evidence Acquisition",
            acquisition_ok,
        )

    # --------------------------------------------------------
    # Financial
    # --------------------------------------------------------

    def print_financial_summary(self) -> None:

        heading("Financial Summary")

        financial = self.payload.get(
            "financial",
            {},
        )

        print(
            "Balance       :",
            financial.get("balance"),
        )

        print(
            "Equity        :",
            financial.get("equity"),
        )

        print(
            "Margin        :",
            financial.get("margin"),
        )

        print(
            "Buying Power  :",
            financial.get("buying_power"),
        )

        required = [
            "balance",
            "equity",
            "buying_power",
        ]

        if args.provider == "mt5":
            required.append("margin")

        financial_ok = all(
            financial.get(field) is not None
            for field in required
        )

        self.report.add(
            "Financial",
            financial_ok,
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def print_statistics(self) -> None:

        heading("Evidence Statistics")

        print(
            "Symbols       :",
            safe_len(
                self.payload.get("symbols"),
            ),
        )

        print(
            "Positions     :",
            safe_len(
                self.payload.get("positions"),
            ),
        )

        print(
            "Orders        :",
            safe_len(
                self.payload.get("orders"),
            ),
        )

        print(
            "Deals         :",
            safe_len(
                self.payload.get("deals"),
            ),
        )

        print(
            "History Orders:",
            safe_len(
                self.payload.get("history"),
            ),
        )

        self.report.add(
            "Statistics",
            True,
        )


        # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------

    def shutdown(self) -> None:

        print()

        print(LINE)
        print("Shutdown")
        print(LINE)

        if (
            self.adapter is None
            or not self.connected
        ):

            print("disconnect()    : skipped")

            return

        try:

            self.adapter.disconnect()

            self.connected = False

            print("disconnect()    : ✓")

            self.report.add(
                "Shutdown",
                True,
            )

        except Exception as exc:

            print("disconnect()    : ✗")

            print(exc)

            self.report.add(
                "Shutdown",
                False,
                str(exc),
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def print_summary(self) -> None:

        print()

        print(LINE)
        print("OVERALL RESULT")
        print(LINE)

        for check in self.report.checks:

            print(
                f"{check.name:<28}",
                "PASS" if check.passed else "FAIL",
            )

        print()

        print(
            "Checks Passed :",
            self.report.succeeded,
        )

        print(
            "Checks Failed :",
            self.report.failed,
        )

        print(
            "Total Checks  :",
            self.report.total,
        )

        print()

        print(
            "Elapsed Time  :",
            f"{self.report.elapsed:.3f} seconds",
        )

        print()

        if self.report.passed:

            print("RESULT : PASS")

        else:

            print("RESULT : FAIL")

        print(LINE)


# ============================================================
# Main
# ============================================================


def main() -> None:

    diagnostics = DesktopDiagnostics()

    diagnostics.run()


if __name__ == "__main__":

    main()