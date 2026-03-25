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
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
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

function getSeriesStats(points: EquityCurvePoint[]) {
  if (!points.length) {
    return {
      start: 0,
      end: 0,
      min: 0,
      max: 0,
      netChange: 0,
      positiveTrades: 0,
      negativeTrades: 0,
      avgTradePnl: 0,
      maxDrawdown: 0,
      peakValue: 0,
      troughValue: 0,
      peakIndex: 0,
      troughIndex: 0,
    };
  }

  const cumulative = points.map((p) => p.cumulative_pnl);
  const pnl = points.map((p) => p.net_pnl);

  let runningPeak = cumulative[0] ?? 0;
  let runningPeakIndex = 0;
  let maxDrawdown = 0;
  let troughValue = cumulative[0] ?? 0;
  let troughIndex = 0;
  let peakValueAtDrawdown = cumulative[0] ?? 0;
  let peakIndexAtDrawdown = 0;

  for (let i = 0; i < cumulative.length; i += 1) {
    const value = cumulative[i] ?? 0;

    if (value > runningPeak) {
      runningPeak = value;
      runningPeakIndex = i;
    }

    const drawdown = runningPeak - value;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
      troughValue = value;
      troughIndex = i;
      peakValueAtDrawdown = runningPeak;
      peakIndexAtDrawdown = runningPeakIndex;
    }
  }

  return {
    start: cumulative[0] ?? 0,
    end: cumulative[cumulative.length - 1] ?? 0,
    min: Math.min(...cumulative),
    max: Math.max(...cumulative),
    netChange: (cumulative[cumulative.length - 1] ?? 0) - (cumulative[0] ?? 0),
    positiveTrades: pnl.filter((x) => x > 0).length,
    negativeTrades: pnl.filter((x) => x < 0).length,
    avgTradePnl: pnl.length ? pnl.reduce((sum, x) => sum + x, 0) / pnl.length : 0,
    maxDrawdown,
    peakValue: peakValueAtDrawdown,
    troughValue,
    peakIndex: peakIndexAtDrawdown,
    troughIndex,
  };
}

function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold">{value}</div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
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

  const width = 960;
  const height = 300;
  const padding = 28;

  const values = points.map((p) => p.cumulative_pnl);
  const minValue = Math.min(...values, 0);
  const maxValue = Math.max(...values, 0);
  const range = maxValue - minValue || 1;

  const stats = getSeriesStats(points);
  const firstPoint = points[0];
  const lastPoint = points[points.length - 1];
  const peakPoint = points[stats.peakIndex] || firstPoint;
  const troughPoint = points[stats.troughIndex] || firstPoint;

  const xFor = (index: number) => {
    if (points.length === 1) return width / 2;
    return padding + (index / (points.length - 1)) * (width - padding * 2);
  };

  const yFor = (value: number) => {
    return padding + ((maxValue - value) / range) * (height - padding * 2);
  };

  const linePath = points
    .map((point, i) => `${i === 0 ? "M" : "L"} ${xFor(i)} ${yFor(point.cumulative_pnl)}`)
    .join(" ");

  const areaPath = [
    linePath,
    `L ${xFor(points.length - 1)} ${height - padding}`,
    `L ${xFor(0)} ${height - padding}`,
    "Z",
  ].join(" ");

  const zeroY = yFor(0);

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-2xl">
          <h2 className="text-xl font-semibold">{title}</h2>
          <div className="mt-1 text-sm text-slate-500">
            Ordered by trade open time and cumulative net PnL across the claim evidence set.
          </div>
        </div>

        <div className="grid gap-2 text-sm sm:grid-cols-3">
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">Start</div>
            <div className="mt-1 font-semibold">{formatNumber(stats.start, 4)}</div>
          </div>
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">End</div>
            <div className="mt-1 font-semibold">{formatNumber(stats.end, 4)}</div>
          </div>
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">Points</div>
            <div className="mt-1 font-semibold">{points.length}</div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Equity Low"
          value={formatNumber(stats.min, 4)}
          hint="Lowest cumulative point"
        />
        <StatCard
          label="Equity High"
          value={formatNumber(stats.max, 4)}
          hint="Highest cumulative point"
        />
        <StatCard
          label="Max Drawdown"
          value={formatNumber(stats.maxDrawdown, 4)}
          hint="Peak-to-trough decline"
        />
        <StatCard
          label="Average Trade PnL"
          value={formatNumber(stats.avgTradePnl, 4)}
          hint="Mean net PnL per row"
        />
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Net Change"
          value={formatNumber(stats.netChange, 4)}
          hint="End minus start"
        />
        <StatCard
          label="Positive Trades"
          value={stats.positiveTrades}
          hint="Rows with positive PnL"
        />
        <StatCard
          label="Negative Trades"
          value={stats.negativeTrades}
          hint="Rows with negative PnL"
        />
        <StatCard
          label="Win/Loss Balance"
          value={`${stats.positiveTrades}/${stats.negativeTrades}`}
          hint="Positive vs negative trade rows"
        />
      </div>

      <div className="mt-5 overflow-x-auto rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-[300px] min-w-[760px] w-full">
          <line
            x1={padding}
            y1={zeroY}
            x2={width - padding}
            y2={zeroY}
            stroke="#cbd5e1"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />

          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={height - padding}
            stroke="#e2e8f0"
            strokeWidth="1"
          />

          <line
            x1={padding}
            y1={height - padding}
            x2={width - padding}
            y2={height - padding}
            stroke="#e2e8f0"
            strokeWidth="1"
          />

          <path
            d={areaPath}
            fill="rgba(15, 23, 42, 0.08)"
            stroke="none"
          />

          <path
            d={linePath}
            fill="none"
            stroke="#0f172a"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {stats.maxDrawdown > 0 ? (
            <line
              x1={xFor(stats.peakIndex)}
              y1={yFor(stats.peakValue)}
              x2={xFor(stats.troughIndex)}
              y2={yFor(stats.troughValue)}
              stroke="#94a3b8"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
          ) : null}

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

      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">First point</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{firstPoint.trade_id} · {firstPoint.symbol} · {formatDateTime(firstPoint.opened_at)}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Last point</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{lastPoint.trade_id} · {lastPoint.symbol} · {formatDateTime(lastPoint.opened_at)}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Drawdown peak</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{peakPoint.trade_id} · {peakPoint.symbol} · {formatDateTime(peakPoint.opened_at)}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Drawdown trough</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{troughPoint.trade_id} · {troughPoint.symbol} · {formatDateTime(troughPoint.opened_at)}
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-sm font-semibold text-slate-900">Risk path note</div>
        <div className="mt-2 text-sm text-slate-600">
          The most important additional statistic on an equity curve is usually max drawdown, because it
          shows the deepest peak-to-trough decline experienced along the path, not just the final result.
          Equity high and low help frame the range, but drawdown gives the stronger credibility signal for
          risk-aware review.
        </div>
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
              <tr key={`${point.trade_id}-${point.index}`} className="border-b last:border-0">
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