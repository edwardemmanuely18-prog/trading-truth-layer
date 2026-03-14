type EquityCurvePoint = {
  index: number;
  trade_id: number;
  member_id: number;
  symbol: string;
  opened_at: string;
  net_pnl: number;
  cumulative_pnl: number;
};

type Props = {
  title?: string;
  points: EquityCurvePoint[];
};

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(digits);
}

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function EquityCurveChart({
  title = "Equity Curve",
  points,
}: Props) {
  if (!points.length) {
    return (
      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold">{title}</h2>
        <div className="mt-4 text-sm text-slate-500">No equity curve data available.</div>
      </div>
    );
  }

  const width = 900;
  const height = 280;
  const padding = 28;

  const values = points.map((p) => p.cumulative_pnl);
  const minValue = Math.min(...values, 0);
  const maxValue = Math.max(...values, 0);
  const range = maxValue - minValue || 1;

  const xFor = (index: number) => {
    if (points.length === 1) return width / 2;
    return padding + (index / (points.length - 1)) * (width - padding * 2);
  };

  const yFor = (value: number) => {
    return padding + ((maxValue - value) / range) * (height - padding * 2);
  };

  const path = points
    .map((point, i) => `${i === 0 ? "M" : "L"} ${xFor(i)} ${yFor(point.cumulative_pnl)}`)
    .join(" ");

  const lastPoint = points[points.length - 1];
  const firstPoint = points[0];

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">{title}</h2>
          <div className="mt-1 text-sm text-slate-500">
            Ordered by trade open time and cumulative net PnL.
          </div>
        </div>

        <div className="grid gap-2 text-sm sm:grid-cols-3">
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">Start</div>
            <div className="mt-1 font-semibold">{formatNumber(firstPoint.cumulative_pnl)}</div>
          </div>
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">End</div>
            <div className="mt-1 font-semibold">{formatNumber(lastPoint.cumulative_pnl)}</div>
          </div>
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">Points</div>
            <div className="mt-1 font-semibold">{points.length}</div>
          </div>
        </div>
      </div>

      <div className="mt-5 overflow-x-auto rounded-xl border bg-slate-50 p-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-[280px] min-w-[700px] w-full">
          <line
            x1={padding}
            y1={yFor(0)}
            x2={width - padding}
            y2={yFor(0)}
            stroke="#cbd5e1"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />

          <path
            d={path}
            fill="none"
            stroke="#0f172a"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {points.map((point, i) => (
            <g key={`${point.trade_id}-${i}`}>
              <circle
                cx={xFor(i)}
                cy={yFor(point.cumulative_pnl)}
                r="4"
                fill="#0f172a"
              >
                <title>{`Trade #${point.trade_id} | ${point.symbol} | PnL ${point.net_pnl} | Cum ${point.cumulative_pnl}`}</title>
              </circle>
            </g>
          ))}
        </svg>
      </div>

      <div className="mt-5 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="px-3 py-2">#</th>
              <th className="px-3 py-2">Trade ID</th>
              <th className="px-3 py-2">Opened</th>
              <th className="px-3 py-2">Symbol</th>
              <th className="px-3 py-2">PnL</th>
              <th className="px-3 py-2">Cumulative</th>
            </tr>
          </thead>
          <tbody>
            {points.map((point) => (
              <tr key={point.trade_id} className="border-b last:border-0">
                <td className="px-3 py-2">{point.index}</td>
                <td className="px-3 py-2">{point.trade_id}</td>
                <td className="px-3 py-2">{formatDateTime(point.opened_at)}</td>
                <td className="px-3 py-2">{point.symbol}</td>
                <td className="px-3 py-2">{formatNumber(point.net_pnl, 4)}</td>
                <td className="px-3 py-2">{formatNumber(point.cumulative_pnl, 4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}