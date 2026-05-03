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

export default function TradeTable({
  trades,
  canWriteTrades = false,
  onEditTrade,
  onDeleteTrade,
  deletingTradeId = null,
}: Props) {
  const showActions = canWriteTrades && (Boolean(onEditTrade) || Boolean(onDeleteTrade));

  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-slate-600">
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
            <th className="px-4 py-3">Strategy</th>
            <th className="px-4 py-3">Source</th>
            {showActions ? <th className="px-4 py-3">Actions</th> : null}
          </tr>
        </thead>
        <tbody>
          {trades.length === 0 ? (
            <tr>
              <td className="px-4 py-6 text-slate-500" colSpan={showActions ? 14 : 13}>
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
                <td className="px-4 py-3">{trade.tags?.join(", ") || "" || "—"}</td>
                <td className="px-3 py-2">
                  {trade.tags?.join(", ") || "" ? (
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-lg">
                      {trade.tags?.join(", ") || ""}
                    </span>
                  ) : "—"}
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