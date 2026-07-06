import { Trade } from "../lib/api";

type Props = {
  trades: Trade[];
  canWriteTrades?: boolean;
  onEditTrade?: (trade: Trade) => void;
  onDeleteTrade?: (trade: Trade) => void;
  deletingTradeId?: number | null;
};

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value?: number | null, digits = 4) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(digits);
}

function getTier(trade: Trade) {

    const source =
        (trade.source_system || "").toUpperCase();

    /*
    --------------------------------------------------
    Tier 1
    Live broker synchronization
    --------------------------------------------------
    */

    if (
        source.includes("MT5") ||
        source.includes("MT4") ||
        source.includes("IBKR") ||
        source.includes("BROKER") ||
        source.includes("SYNC")
    ) {
        return {
            label: "🟢 Tier I",
            color:
                "bg-green-100 text-green-700 border-green-300",
        };
    }

    /*
    --------------------------------------------------
    Tier 2
    Imported statements
    --------------------------------------------------
    */

    if (
        source.includes("CSV") ||
        source.includes("IMPORT")
    ) {
        return {
            label: "🟡 Tier II",
            color:
                "bg-amber-100 text-amber-700 border-amber-300",
        };
    }

    /*
    --------------------------------------------------
    Tier 3
    Manual / edited
    --------------------------------------------------
    */

    return {
        label: "🔴 Tier III",
        color:
            "bg-red-100 text-red-700 border-red-300",
    };
}

export default function TradeTable({
  trades,
  canWriteTrades = false,
  onEditTrade,
  onDeleteTrade,
  deletingTradeId = null,
}: Props) {
  const showActions = canWriteTrades && (Boolean(onEditTrade) || Boolean(onDeleteTrade));

  return (
    <div className="overflow-x-auto overflow-y-auto max-h-[750px] rounded-2xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="sticky top-0 z-10 bg-slate-50 text-left text-slate-600 shadow-sm">
          <tr>
            <th className="px-4 py-3">ID</th>
            <th className="px-4 py-3">Member</th>
            <th className="px-4 py-3">Symbol</th>
            <th className="px-4 py-3">Side</th>
            <th className="px-4 py-3">Opened</th>
            <th className="px-4 py-3">Closed</th>
            <th className="px-4 py-3">Entry</th>
            <th className="px-4 py-3">Exit</th>
            <th className="px-4 py-3">Qty</th>
            <th className="px-4 py-3">Net PnL</th>
            <th className="px-4 py-3">Currency</th>
            <th className="w-36 px-4 py-3 whitespace-nowrap">
                Trust Tier
            </th>
            <th className="px-4 py-3">Strategy</th>
            <th className="px-4 py-3">Source</th>
            {showActions ? <th className="px-4 py-3">Actions</th> : null}
          </tr>
        </thead>
        <tbody>
          {trades.length === 0 ? (
            <tr>
              <td className="px-4 py-6 text-slate-500" colSpan={showActions ? 15 : 14}>
                No trades found in this workspace.
              </td>
            </tr>
          ) : (
            trades.map((trade) => (
              <tr key={trade.id} className="border-t border-slate-200">
                <td className="px-4 py-3 font-medium">{trade.id}</td>
                <td className="px-4 py-3">{trade.member_id}</td>
                <td className="px-4 py-3">{trade.symbol || "—"}</td>
                <td className="px-4 py-3">{trade.side || "—"}</td>
                <td className="px-4 py-3">{formatDateTime(trade.opened_at)}</td>
                <td className="px-4 py-3">{formatDateTime(trade.closed_at)}</td>
                <td className="px-4 py-3">{formatNumber(trade.entry_price)}</td>
                <td className="px-4 py-3">{formatNumber(trade.exit_price)}</td>
                <td className="px-4 py-3">{formatNumber(trade.quantity)}</td>
                <td className="px-4 py-3">{formatNumber(trade.net_pnl)}</td>
                <td className="px-4 py-3">{trade.currency || "—"}</td>
                <td className="w-36 px-4 py-3 whitespace-nowrap">

                    {(() => {

                        const tier = getTier(trade);

                        return (

                            <span
                                className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold whitespace-nowrap ${tier.color}`}
                            >
                                {tier.label}
                            </span>

                        );

                    })()}

                </td>

                <td className="px-4 py-3">
                  {trade.strategy_tag ? (
                    <span className="px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded-lg">
                      {trade.strategy_tag}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="px-4 py-3">{trade.source_system || "—"}</td>
                {showActions ? (
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      {onEditTrade ? (
                        <button
                          type="button"
                          onClick={() => onEditTrade(trade)}
                          className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                        >
                          Edit
                        </button>
                      ) : null}

                      {onDeleteTrade ? (
                        <button
                          type="button"
                          onClick={() => onDeleteTrade(trade)}
                          disabled={deletingTradeId === trade.id}
                          className="rounded-lg border border-red-300 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {deletingTradeId === trade.id ? "Deleting..." : "Delete"}
                        </button>
                      ) : null}
                    </div>
                  </td>
                ) : null}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}