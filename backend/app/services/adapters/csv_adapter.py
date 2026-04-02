import csv
import io
from datetime import datetime

from app.services.adapters.base import NormalizedTradeRow


class CSVTradeAdapter:
    STANDARD_REQUIRED = {
        "member_id",
        "symbol",
        "side",
        "opened_at",
        "entry_price",
        "quantity",
        "currency",
    }

    AURUM_EXTENDED = {
        "member_id",
        "symbol",
        "side",
        "opened_at",
        "entry_price",
        "quantity",
        "currency",
        "net_pnl",
        "strategy_tag",
        "source_system",
    }

    @staticmethod
    def _parse_optional_float(value):
        if value is None:
            return None
        text = str(value).strip()
        if text == "":
            return None
        return float(text)

    @staticmethod
    def _parse_optional_datetime(value):
        if value is None:
            return None
        text = str(value).strip()
        if text == "":
            return None
        return datetime.fromisoformat(text)

    @staticmethod
    def _compute_net_pnl(side: str, entry_price: float, exit_price: float | None, quantity: float):
        if exit_price is None:
            return None

        normalized_side = side.strip().upper()

        if normalized_side == "BUY":
            return (exit_price - entry_price) * quantity

        if normalized_side == "SELL":
            return (entry_price - exit_price) * quantity

        return None

    def detect_format(self, fieldnames: list[str] | None) -> str:
        if not fieldnames:
            raise ValueError("CSV file has no header row")

        fieldnames_set = set(fieldnames)

        if not self.STANDARD_REQUIRED.issubset(fieldnames_set):
            missing = self.STANDARD_REQUIRED - fieldnames_set
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        if self.AURUM_EXTENDED.issubset(fieldnames_set):
            return "aurum_extended"

        return "standard"

    def parse(self, content: bytes) -> tuple[list[NormalizedTradeRow], str]:
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))

        format_type = self.detect_format(reader.fieldnames)

        rows: list[NormalizedTradeRow] = []

        for idx, row in enumerate(reader, start=2):
            try:
                side = row["side"].strip().upper()
                opened_at = datetime.fromisoformat(row["opened_at"])
                entry_price = float(row["entry_price"])
                quantity = float(row["quantity"])
                closed_at = self._parse_optional_datetime(row.get("closed_at"))
                exit_price = self._parse_optional_float(row.get("exit_price"))

                supplied_net_pnl = self._parse_optional_float(row.get("net_pnl"))
                computed_net_pnl = self._compute_net_pnl(
                    side=side,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    quantity=quantity,
                )

                normalized = NormalizedTradeRow(
                    member_id=int(row["member_id"]),
                    symbol=row["symbol"].strip().upper(),
                    side=side,
                    opened_at=opened_at,
                    entry_price=entry_price,
                    quantity=quantity,
                    currency=row["currency"].strip().upper(),
                    closed_at=closed_at,
                    exit_price=exit_price,
                    net_pnl=supplied_net_pnl if supplied_net_pnl is not None else computed_net_pnl,
                    strategy_tag=(row.get("strategy_tag") or "").strip() or None,
                    source_system=(row.get("source_system") or "").strip() or None,
                )
                rows.append(normalized)
            except Exception as e:
                raise ValueError(f"Row {idx}: {str(e)}") from e

        return rows, format_type