import { Trade } from "../lib/api";

type Props = {
  trades: Trade[];
};

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
            <th className="px-4 py-3">Entry</th>
            <th className="px-4 py-3">Qty</th>
            <th className="px-4 py-3">Net PnL</th>
            <th className="px-4 py-3">Strategy</th>
            <th className="px-4 py-3">Source</th>
          </tr>
        </thead>
        <tbody>
          {trades.length === 0 ? (
            <tr>
              <td className="px-4 py-4 text-slate-500" colSpan={10}>
                No trades found in this workspace.
              </td>
            </tr>
          ) : (
            trades.map((trade) => (
              <tr key={trade.id} className="border-t border-slate-200">
                <td className="px-4 py-3">{trade.id}</td>
                <td className="px-4 py-3">{trade.member_id}</td>
                <td className="px-4 py-3">{trade.symbol}</td>
                <td className="px-4 py-3">{trade.side}</td>
                <td className="px-4 py-3">
                  {new Date(trade.opened_at).toLocaleString()}
                </td>
                <td className="px-4 py-3">{trade.entry_price}</td>
                <td className="px-4 py-3">{trade.quantity}</td>
                <td className="px-4 py-3">{trade.net_pnl ?? "-"}</td>
                <td className="px-4 py-3">{trade.strategy_tag ?? "-"}</td>
                <td className="px-4 py-3">{trade.source_system ?? "-"}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}