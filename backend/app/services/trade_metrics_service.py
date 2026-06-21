from datetime import datetime

from app.models.trade import Trade

from app.services.claim_integrity_engine import (
    coerce_trade_opened_at,
)


def compute_trade_metrics(trades: list[Trade]):
    trade_count = len(trades)

    pnl_values = [
        t.net_pnl
        for t in trades
        if t.net_pnl is not None
    ]

    if not pnl_values:
        return {
            "trade_count": trade_count,
            "net_pnl": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
        }

    wins = [x for x in pnl_values if x > 0]
    losses = [x for x in pnl_values if x < 0]

    gross_profit = sum(wins)
    gross_loss_abs = abs(sum(losses))

    net_pnl = sum(pnl_values)

    win_rate = (
        len(wins)
        / len(pnl_values)
        if pnl_values
        else 0.0
    )

    if gross_loss_abs == 0:
        profit_factor = (
            gross_profit
            if gross_profit > 0
            else 0.0
        )
    else:
        profit_factor = (
            gross_profit
            / gross_loss_abs
        )

    return {
        "trade_count": trade_count,
        "net_pnl": round(net_pnl, 4),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4),
        "best_trade": round(max(pnl_values), 4),
        "worst_trade": round(min(pnl_values), 4),
    }


def build_equity_curve(
    trades: list[Trade]
):
    ordered = sorted(
        trades,
        key=lambda t: (
            coerce_trade_opened_at(
                t.opened_at
            ) or datetime.min,
            t.id,
        ),
    )

    cumulative = 0.0

    points = []

    for index, trade in enumerate(
        ordered,
        start=1,
    ):
        pnl = (
            float(trade.net_pnl)
            if trade.net_pnl is not None
            else 0.0
        )

        cumulative += pnl

        opened_at_value = (
            coerce_trade_opened_at(
                trade.opened_at
            )
        )

        opened_at_iso = (
            opened_at_value.isoformat()
            if isinstance(
                opened_at_value,
                datetime,
            )
            else str(
                trade.opened_at
            )
        )

        points.append(
            {
                "index": index,
                "trade_id": trade.id,
                "member_id": trade.member_id,
                "symbol": trade.symbol,
                "opened_at": opened_at_iso,
                "net_pnl": round(
                    pnl,
                    4,
                ),
                "cumulative_pnl": round(
                    cumulative,
                    4,
                ),
            }
        )

    return {
        "point_count": len(points),
        "starting_equity": (
            0.0
            if not points
            else points[0][
                "cumulative_pnl"
            ]
        ),
        "ending_equity": round(
            cumulative,
            4,
        ),
        "curve": points,
    }


def compute_drawdown_stats(
    points: list[dict]
):
    if not points:
        return {
            "max_drawdown": 0.0,
            "peak_cumulative": 0.0,
            "trough_cumulative": 0.0,
            "peak_point": None,
            "trough_point": None,
            "drawdown_peak_point": None,
            "drawdown_trough_point": None,
            "has_drawdown": False,
            "net_change": 0.0,
            "peak_equals_trough": False,
        }

    peak_point = max(
        points,
        key=lambda p:
        float(
            p.get(
                "cumulative_pnl",
                0.0,
            )
        ),
    )

    trough_point = min(
        points,
        key=lambda p:
        float(
            p.get(
                "cumulative_pnl",
                0.0,
            )
        ),
    )

    running_peak = float("-inf")

    max_drawdown = 0.0

    drawdown_peak_point = None
    drawdown_trough_point = None

    current_peak_point = None

    for point in points:

        current = float(
            point.get(
                "cumulative_pnl",
                0.0,
            )
        )

        if current > running_peak:
            running_peak = current
            current_peak_point = point

        drawdown = (
            running_peak
            - current
        )

        if drawdown > max_drawdown:
            max_drawdown = drawdown
            drawdown_peak_point = (
                current_peak_point
            )
            drawdown_trough_point = (
                point
            )

    start_value = float(
        points[0].get(
            "cumulative_pnl",
            0.0,
        )
    )

    end_value = float(
        points[-1].get(
            "cumulative_pnl",
            0.0,
        )
    )

    return {
        "max_drawdown": round(
            max_drawdown,
            4,
        ),
        "peak_cumulative": round(
            float(
                peak_point.get(
                    "cumulative_pnl",
                    0.0,
                )
            ),
            4,
        ),
        "trough_cumulative": round(
            float(
                trough_point.get(
                    "cumulative_pnl",
                    0.0,
                )
            ),
            4,
        ),
        "peak_point": peak_point,
        "trough_point": trough_point,
        "drawdown_peak_point":
            drawdown_peak_point,
        "drawdown_trough_point":
            drawdown_trough_point,
        "has_drawdown":
            max_drawdown > 0,
        "net_change":
            round(
                end_value
                - start_value,
                4,
            ),
        "peak_equals_trough":
            peak_point.get("index")
            ==
            trough_point.get("index"),
    }