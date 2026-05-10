import csv
import io
from datetime import datetime

from app.services.adapters.base import (
    NormalizedTradeRow,
)


class IBKRTradeAdapter:
    """
    Interactive Brokers Flex Query CSV adapter.
    """

    REQUIRED_COLUMNS = {
        "Symbol",
        "Buy/Sell",
        "Quantity",
        "TradePrice",
        "Date/Time",
    }

    @staticmethod
    def _safe_float(value, default=None):
        if value is None:
            return default

        text = str(value).replace(",", "").strip()

        if text == "":
            return default

        return float(text)

    @staticmethod
    def _parse_datetime(value: str):
        value = value.strip()

        formats = [
            "%Y-%m-%d, %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y%m%d  %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                pass

        raise ValueError(
            f"Unsupported IBKR datetime format: {value}"
        )

    def detect_format(self, fieldnames):
        if not fieldnames:
            raise ValueError(
                "IBKR CSV has no header row"
            )

        missing = (
            self.REQUIRED_COLUMNS
            - set(fieldnames)
        )

        if missing:
            raise ValueError(
                "Invalid IBKR export. Missing columns: "
                + ", ".join(sorted(missing))
            )

    def parse(
        self,
        content: bytes,
    ) -> tuple[list[NormalizedTradeRow], str]:

        text = content.decode(
            "utf-8",
            errors="ignore",
        )

        reader = csv.DictReader(
            io.StringIO(text)
        )

        self.detect_format(
            reader.fieldnames
        )

        rows: list[NormalizedTradeRow] = []

        for idx, row in enumerate(reader, start=2):
            try:
                symbol = (
                    row["Symbol"]
                    .strip()
                    .upper()
                )

                side = (
                    row["Buy/Sell"]
                    .strip()
                    .upper()
                )

                quantity = abs(
                    self._safe_float(
                        row["Quantity"],
                        0,
                    )
                )

                entry_price = self._safe_float(
                    row["TradePrice"],
                    0,
                )

                opened_at = self._parse_datetime(
                    row["Date/Time"]
                )

                currency = (
                    row.get("Currency", "USD")
                    .strip()
                    .upper()
                )

                net_pnl = self._safe_float(
                    row.get("Realized P/L"),
                    None,
                )

                rows.append(
                    NormalizedTradeRow(
                        member_id=999,
                        symbol=symbol,
                        side=side,
                        opened_at=opened_at,
                        entry_price=entry_price,
                        quantity=quantity,
                        currency=currency,
                        net_pnl=net_pnl,
                        strategy_tag=None,
                        source_system="IBKR",
                    )
                )

            except Exception as e:
                raise ValueError(
                    f"IBKR row {idx}: {str(e)}"
                ) from e

        return rows, "ibkr"