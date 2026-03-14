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
                opened_at = datetime.fromisoformat(row["opened_at"])
                normalized = NormalizedTradeRow(
                    member_id=int(row["member_id"]),
                    symbol=row["symbol"].strip().upper(),
                    side=row["side"].strip().upper(),
                    opened_at=opened_at,
                    entry_price=float(row["entry_price"]),
                    quantity=float(row["quantity"]),
                    currency=row["currency"].strip().upper(),
                    net_pnl=self._parse_optional_float(row.get("net_pnl")),
                    strategy_tag=(row.get("strategy_tag") or "").strip() or None,
                    source_system=(row.get("source_system") or "").strip() or None,
                )
                rows.append(normalized)
            except Exception as e:
                raise ValueError(f"Row {idx}: {str(e)}") from e

        return rows, format_type