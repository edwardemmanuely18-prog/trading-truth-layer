"use client";

import { useMemo } from "react";

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

function formatDateShort(value?: string | null) {
  if (!value) return "—";
  try {
    const date = new Date(value);
    return date.toLocaleDateString();
  } catch {
    return value;
  }
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
      maxDrawdown: 0,
      peakIndex: 0,
      troughIndex: 0,
      peakValue: 0,
      troughValue: 0,
      positiveTrades: 0,
      negativeTrades: 0,
      avgTradePnl: 0,
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
    maxDrawdown,
    peakIndex: peakIndexAtDrawdown,
    troughIndex,
    peakValue: peakValueAtDrawdown,
    troughValue,
    positiveTrades: pnl.filter((x) => x > 0).length,
    negativeTrades: pnl.filter((x) => x < 0).length,
    avgTradePnl: pnl.length ? pnl.reduce((sum, x) => sum + x, 0) / pnl.length : 0,
  };
}

function StatTile({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-slate-900">{value}</div>
      {hint ? <div className="mt-1 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

export default function EquityCurveChart({
  title = "Equity Curve",
  points,
}: Props) {
  const width = 960;
  const height = 380;
  const padding = { top: 28, right: 28, bottom: 52, left: 72 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const stats = useMemo(() => getSeriesStats(points), [points]);

  const values = points.map((p) => p.cumulative_pnl);
  const minValue = Math.min(...values, 0);
  const maxValue = Math.max(...values, 0);
  const range = maxValue - minValue || 1;

  const firstPoint = points[0] ?? null;
  const lastPoint = points[points.length - 1] ?? null;
  const peakPoint = points[stats.peakIndex] ?? null;
  const troughPoint = points[stats.troughIndex] ?? null;

  const xFor = (index: number) => {
    if (points.length <= 1) return padding.left + chartWidth / 2;
    return padding.left + (index / (points.length - 1)) * chartWidth;
  };

  const yFor = (value: number) => {
    return padding.top + ((maxValue - value) / range) * chartHeight;
  };

  const yTicks = 5;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) => {
    return minValue + ((maxValue - minValue) / yTicks) * i;
  });

  const xTicks = points.length <= 2
    ? [0, Math.max(points.length - 1, 0)]
    : [0, Math.floor((points.length - 1) / 2), points.length - 1];

  const linePath = points
    .map((point, i) => `${i === 0 ? "M" : "L"} ${xFor(i)} ${yFor(point.cumulative_pnl)}`)
    .join(" ");

  const areaPath = [
    linePath,
    `L ${xFor(points.length - 1)} ${height - padding.bottom}`,
    `L ${xFor(0)} ${height - padding.bottom}`,
    "Z",
  ].join(" ");

  const drawdownShadePath =
    peakPoint && troughPoint && stats.maxDrawdown > 0
      ? [
          `M ${xFor(stats.peakIndex)} ${yFor(stats.peakValue)}`,
          `L ${xFor(stats.troughIndex)} ${yFor(stats.troughValue)}`,
          `L ${xFor(stats.troughIndex)} ${yFor(stats.peakValue)}`,
          `L ${xFor(stats.peakIndex)} ${yFor(stats.peakValue)}`,
          "Z",
        ].join(" ")
      : null;

  const peakX = xFor(stats.peakIndex);
  const peakY = yFor(stats.peakValue);
  const troughX = xFor(stats.troughIndex);
  const troughY = yFor(stats.troughValue);

  if (!points.length) {
    return (
      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold">{title}</h2>
        <div className="mt-4 text-sm text-slate-500">No equity curve data available.</div>
      </div>
    );
  }

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
            <div className="text-slate-500">Max Drawdown</div>
            <div className="mt-1 font-semibold">{formatNumber(stats.maxDrawdown, 4)}</div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatTile
          label="Equity High"
          value={formatNumber(stats.max, 4)}
          hint="Highest cumulative point"
        />
        <StatTile
          label="Equity Low"
          value={formatNumber(stats.min, 4)}
          hint="Lowest cumulative point"
        />
        <StatTile
          label="Average Trade PnL"
          value={formatNumber(stats.avgTradePnl, 4)}
          hint="Mean net PnL per trade"
        />
        <StatTile
          label="Positive / Negative"
          value={`${stats.positiveTrades}/${stats.negativeTrades}`}
          hint="Trade count balance"
        />
      </div>

      <div className="mt-5 overflow-x-auto rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-[380px] min-w-[760px] w-full">
          <defs>
            <linearGradient id="equityAreaFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(15,23,42,0.14)" />
              <stop offset="100%" stopColor="rgba(15,23,42,0.03)" />
            </linearGradient>
          </defs>

          {yTickValues.map((tick, i) => {
            const y = yFor(tick);
            return (
              <g key={`y-tick-${i}`}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#E2E8F0"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 12}
                  y={y + 4}
                  textAnchor="end"
                  className="fill-slate-500 text-[11px]"
                >
                  {formatNumber(tick, 1)}
                </text>
              </g>
            );
          })}

          {xTicks.map((tickIndex) => {
            const point = points[tickIndex];
            if (!point) return null;
            const x = xFor(tickIndex);

            return (
              <g key={`x-tick-${tickIndex}`}>
                <line
                  x1={x}
                  y1={padding.top}
                  x2={x}
                  y2={height - padding.bottom}
                  stroke="#F1F5F9"
                  strokeWidth="1"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 18}
                  textAnchor="middle"
                  className="fill-slate-500 text-[11px]"
                >
                  {point.index}
                </text>
                <text
                  x={x}
                  y={height - padding.bottom + 32}
                  textAnchor="middle"
                  className="fill-slate-400 text-[10px]"
                >
                  {formatDateShort(point.opened_at)}
                </text>
              </g>
            );
          })}

          <line
            x1={padding.left}
            y1={padding.top}
            x2={padding.left}
            y2={height - padding.bottom}
            stroke="#CBD5E1"
            strokeWidth="1"
          />
          <line
            x1={padding.left}
            y1={height - padding.bottom}
            x2={width - padding.right}
            y2={height - padding.bottom}
            stroke="#CBD5E1"
            strokeWidth="1"
          />

          <path d={areaPath} fill="url(#equityAreaFill)" stroke="none" />

          {drawdownShadePath ? (
            <path d={drawdownShadePath} fill="rgba(220,38,38,0.08)" stroke="none" />
          ) : null}

          <path
            d={linePath}
            fill="none"
            stroke="#0F172A"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {stats.maxDrawdown > 0 ? (
            <line
              x1={peakX}
              y1={peakY}
              x2={troughX}
              y2={troughY}
              stroke="#94A3B8"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
          ) : null}

          {points.map((point, i) => (
            <circle
              key={`${point.trade_id}-${i}`}
              cx={xFor(i)}
              cy={yFor(point.cumulative_pnl)}
              r="3.5"
              fill="#0F172A"
            >
              <title>{`Trade #${point.trade_id} | ${point.symbol} | ${formatDateTime(point.opened_at)} | PnL ${point.net_pnl} | Cum ${point.cumulative_pnl}`}</title>
            </circle>
          ))}

          {peakPoint ? (
            <>
              <circle cx={peakX} cy={peakY} r="5" fill="#16A34A" />
              <text x={peakX + 10} y={peakY - 10} className="fill-green-700 text-[11px] font-medium">
                Peak {formatNumber(stats.peakValue, 2)}
              </text>
            </>
          ) : null}

          {troughPoint ? (
            <>
              <circle cx={troughX} cy={troughY} r="5" fill="#DC2626" />
              <text
                x={troughX - 10}
                y={troughY - 10}
                textAnchor="end"
                className="fill-red-700 text-[11px] font-medium"
              >
                Trough {formatNumber(stats.troughValue, 2)}
              </text>
            </>
          ) : null}

          <text
            x={width - padding.right}
            y={padding.top - 6}
            textAnchor="end"
            className="fill-slate-500 text-[11px]"
          >
            Net change {formatNumber(stats.netChange, 4)}
          </text>
        </svg>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">First point</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{firstPoint?.trade_id} · {firstPoint?.symbol} · {formatDateTime(firstPoint?.opened_at)}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Last point</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{lastPoint?.trade_id} · {lastPoint?.symbol} · {formatDateTime(lastPoint?.opened_at)}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Drawdown peak</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{peakPoint?.trade_id} · {peakPoint?.symbol} · {formatDateTime(peakPoint?.opened_at)}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Drawdown trough</div>
          <div className="mt-2 text-sm text-slate-700">
            Trade #{troughPoint?.trade_id} · {troughPoint?.symbol} · {formatDateTime(troughPoint?.opened_at)}
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-sm font-semibold text-slate-900">Risk path note</div>
        <div className="mt-2 text-sm text-slate-600">
          This curve now shows cumulative performance structure, peak-to-trough drawdown path,
          annotated turning points, and sequence context so the evidence surface communicates both
          return and risk with stronger review value.
        </div>
      </div>
    </div>
  );
}