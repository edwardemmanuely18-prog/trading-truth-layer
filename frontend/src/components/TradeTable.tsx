import { Trade } from "../lib/api";

type Props = {
  trades: Trade[];
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

export default function TradeTable({ trades }: Props) {
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
          </tr>
        </thead>
        <tbody>
          {trades.length === 0 ? (
            <tr>
              <td className="px-4 py-6 text-slate-500" colSpan={13}>
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
                <td className="px-4 py-3">{trade.strategy_tag || "—"}</td>
                <td className="px-4 py-3">{trade.source_system || "—"}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}