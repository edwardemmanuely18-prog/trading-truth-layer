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
      minIndex: 0,
      maxIndex: 0,
      netChange: 0,
      maxDrawdown: 0,
      drawdownPeakIndex: null as number | null,
      drawdownTroughIndex: null as number | null,
      drawdownPeakValue: null as number | null,
      drawdownTroughValue: null as number | null,
      positiveTrades: 0,
      negativeTrades: 0,
      avgTradePnl: 0,
    };
  }

  const cumulative = points.map((p) => p.cumulative_pnl);
  const pnl = points.map((p) => p.net_pnl);

  let maxValue = cumulative[0] ?? 0;
  let maxIndex = 0;
  let minValue = cumulative[0] ?? 0;
  let minIndex = 0;

  for (let i = 0; i < cumulative.length; i += 1) {
    const value = cumulative[i] ?? 0;
    if (value > maxValue) {
      maxValue = value;
      maxIndex = i;
    }
    if (value < minValue) {
      minValue = value;
      minIndex = i;
    }
  }

  let runningPeak = cumulative[0] ?? 0;
  let runningPeakIndex = 0;
  let maxDrawdown = 0;
  let drawdownTroughValue: number | null = null;
  let drawdownTroughIndex: number | null = null;
  let drawdownPeakValue: number | null = null;
  let drawdownPeakIndex: number | null = null;

  for (let i = 0; i < cumulative.length; i += 1) {
    const value = cumulative[i] ?? 0;

    if (value > runningPeak) {
      runningPeak = value;
      runningPeakIndex = i;
    }

    const drawdown = runningPeak - value;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
      drawdownTroughValue = value;
      drawdownTroughIndex = i;
      drawdownPeakValue = runningPeak;
      drawdownPeakIndex = runningPeakIndex;
    }
  }

  return {
    start: cumulative[0] ?? 0,
    end: cumulative[cumulative.length - 1] ?? 0,
    min: minValue,
    max: maxValue,
    minIndex,
    maxIndex,
    netChange: (cumulative[cumulative.length - 1] ?? 0) - (cumulative[0] ?? 0),
    maxDrawdown,
    drawdownPeakIndex,
    drawdownTroughIndex,
    drawdownPeakValue,
    drawdownTroughValue,
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

function InfoCard({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-sm text-slate-700">{value}</div>
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

  if (!points.length) {
    return (
      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold">{title}</h2>
        <div className="mt-4 text-sm text-slate-500">No equity curve data available.</div>
      </div>
    );
  }

  const values = points.map((p) => p.cumulative_pnl);
  const minValue = Math.min(...values, 0);
  const maxValue = Math.max(...values, 0);
  const range = maxValue - minValue || 1;

  const firstPoint = points[0] ?? null;
  const lastPoint = points[points.length - 1] ?? null;
  const equityHighPoint = points[stats.maxIndex] ?? null;
  const equityLowPoint = points[stats.minIndex] ?? null;
  const drawdownPeakPoint =
    stats.drawdownPeakIndex !== null ? points[stats.drawdownPeakIndex] ?? null : null;
  const drawdownTroughPoint =
    stats.drawdownTroughIndex !== null ? points[stats.drawdownTroughIndex] ?? null : null;

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

  const xTicks =
    points.length <= 8
      ? points.map((_, i) => i)
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

  const hasDrawdown =
    stats.maxDrawdown > 0 &&
    stats.drawdownPeakIndex !== null &&
    stats.drawdownTroughIndex !== null &&
    stats.drawdownPeakValue !== null &&
    stats.drawdownTroughValue !== null;

  const drawdownShadePath =
    hasDrawdown && drawdownPeakPoint && drawdownTroughPoint
      ? [
          `M ${xFor(stats.drawdownPeakIndex!)} ${yFor(stats.drawdownPeakValue!)}`,
          `L ${xFor(stats.drawdownTroughIndex!)} ${yFor(stats.drawdownTroughValue!)}`,
          `L ${xFor(stats.drawdownTroughIndex!)} ${yFor(stats.drawdownPeakValue!)}`,
          `L ${xFor(stats.drawdownPeakIndex!)} ${yFor(stats.drawdownPeakValue!)}`,
          "Z",
        ].join(" ")
      : null;

  const equityHighX = xFor(stats.maxIndex);
  const equityHighY = yFor(stats.max);
  const drawdownPeakX = hasDrawdown ? xFor(stats.drawdownPeakIndex!) : 0;
  const drawdownPeakY = hasDrawdown ? yFor(stats.drawdownPeakValue!) : 0;
  const drawdownTroughX = hasDrawdown ? xFor(stats.drawdownTroughIndex!) : 0;
  const drawdownTroughY = hasDrawdown ? yFor(stats.drawdownTroughValue!) : 0;

  const showDistinctDrawdownPeak = hasDrawdown && stats.drawdownPeakIndex !== stats.maxIndex;

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
              <stop offset="0%" stopColor="rgba(15,23,42,0.10)" />
              <stop offset="100%" stopColor="rgba(15,23,42,0.02)" />
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
                  stroke="#F1F5F9"
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
                  stroke="#F8FAFC"
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
            stroke="rgba(15,23,42,0.15)"
            strokeWidth="6"
          />

          <path
            d={linePath}
            fill="none"
            stroke="#0F172A"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {hasDrawdown ? (
            <line
              x1={drawdownPeakX}
              y1={drawdownPeakY}
              x2={drawdownTroughX}
              y2={drawdownTroughY}
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

          {equityHighPoint ? (
            <>
              <circle cx={equityHighX} cy={equityHighY} r="5" fill="#16A34A" />
              <text
                x={equityHighX + 10}
                y={equityHighY - 10}
                className="fill-green-600 text-[10px] font-medium"
              >
                High {formatNumber(stats.max, 2)}
              </text>
            </>
          ) : null}

          {showDistinctDrawdownPeak ? (
            <>
              <circle cx={drawdownPeakX} cy={drawdownPeakY} r="4.5" fill="#D97706" />
              <text
                x={drawdownPeakX + 10}
                y={drawdownPeakY + 16}
                className="fill-amber-600 text-[10px] font-medium"
              >
                DD peak {formatNumber(stats.drawdownPeakValue, 2)}
              </text>
            </>
          ) : null}

          {hasDrawdown ? (
            <>
              <circle cx={drawdownTroughX} cy={drawdownTroughY} r="5" fill="#DC2626" />
              <text
                x={drawdownTroughX - 10}
                y={drawdownTroughY - 10}
                textAnchor="end"
                className="fill-red-600 text-[10px] font-medium"
              >
                DD trough {formatNumber(stats.drawdownTroughValue, 2)}
              </text>
            </>
          ) : null}

          <text
            x={width - padding.right}
            y={padding.top - 6}
            textAnchor="end"
            className="fill-slate-400 text-[10px]"
          >
            Net change {formatNumber(stats.netChange, 4)}
          </text>
        </svg>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <InfoCard
          label="First point"
          value={
            <>
              Trade #{firstPoint?.trade_id} · {firstPoint?.symbol} · {formatDateTime(firstPoint?.opened_at)}
            </>
          }
        />

        <InfoCard
          label="Last point"
          value={
            <>
              Trade #{lastPoint?.trade_id} · {lastPoint?.symbol} · {formatDateTime(lastPoint?.opened_at)}
            </>
          }
        />

        <InfoCard
          label="Drawdown peak"
          value={
            hasDrawdown ? (
              <>
                Trade #{drawdownPeakPoint?.trade_id} · {drawdownPeakPoint?.symbol} ·{" "}
                {formatDateTime(drawdownPeakPoint?.opened_at)}
              </>
            ) : (
              "No drawdown event"
            )
          }
        />

        <InfoCard
          label="Drawdown trough"
          value={
            hasDrawdown ? (
              <>
                Trade #{drawdownTroughPoint?.trade_id} · {drawdownTroughPoint?.symbol} ·{" "}
                {formatDateTime(drawdownTroughPoint?.opened_at)}
              </>
            ) : (
              "No drawdown event"
            )
          }
        />
      </div>

      <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-sm font-semibold text-slate-900">Risk path note</div>
        <div className="mt-2 text-sm text-slate-600">
          This curve distinguishes absolute equity high from drawdown peak, highlights the deepest
          peak-to-trough decline only when one actually exists, and shows full sequence context for
          smaller evidence sets so reviewers can inspect both performance progression and risk path quality.
        </div>
      </div>
    </div>
  );
}