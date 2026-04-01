"use client";

import { useEffect, useMemo, useState } from "react";

type EquityCurvePoint = {
  index: number;
  trade_id: number;
  member_id: number;
  symbol: string;
  opened_at: string;
  net_pnl: number;
  cumulative_pnl: number;
};

type EnrichedEquityCurvePoint = EquityCurvePoint & {
  timestamp: number;
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
    return new Date(value).toLocaleDateString(undefined, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return value;
  }
}

function formatDateTick(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleDateString(undefined, {
      day: "2-digit",
      month: "2-digit",
    });
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

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
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

function buildTimeTickIndexes(points: EnrichedEquityCurvePoint[]) {
  return points.map((_, i) => i);
}

function ZoomButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-3 py-2 text-sm font-medium transition ${
        active
          ? "border border-slate-900 bg-slate-900 text-white"
          : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
      }`}
    >
      {label}
    </button>
  );
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
  const width = 1200;
  const height = 460;
  const padding = { top: 28, right: 28, bottom: 70, left: 72 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const orderedPoints = useMemo<EnrichedEquityCurvePoint[]>(() => {
    return [...points]
      .map((point) => ({
        ...point,
        timestamp: new Date(point.opened_at).getTime(),
      }))
      .sort((a, b) => {
        if (a.timestamp !== b.timestamp) return a.timestamp - b.timestamp;
        if (a.index !== b.index) return a.index - b.index;
        return a.trade_id - b.trade_id;
      });
  }, [points]);

  const [zoomStartIndex, setZoomStartIndex] = useState(0);
  const [zoomEndIndex, setZoomEndIndex] = useState(Math.max(orderedPoints.length - 1, 0));
  const [hoveredTradeId, setHoveredTradeId] = useState<number | null>(null);
  const [pinnedTradeId, setPinnedTradeId] = useState<number | null>(null);

  useEffect(() => {
    setZoomStartIndex(0);
    setZoomEndIndex(Math.max(orderedPoints.length - 1, 0));
    setHoveredTradeId(null);
    setPinnedTradeId(null);
  }, [orderedPoints.length]);

  const visiblePoints = useMemo(() => {
    if (!orderedPoints.length) return [];
    const start = clamp(zoomStartIndex, 0, Math.max(orderedPoints.length - 1, 0));
    const end = clamp(zoomEndIndex, start, Math.max(orderedPoints.length - 1, 0));
    return orderedPoints.slice(start, end + 1);
  }, [orderedPoints, zoomStartIndex, zoomEndIndex]);

  const stats = useMemo(() => getSeriesStats(visiblePoints), [visiblePoints]);

  const firstPoint = visiblePoints[0] ?? null;
  const lastPoint = visiblePoints[visiblePoints.length - 1] ?? null;
  const peakPoint = visiblePoints[stats.maxIndex] ?? null;
  const troughPoint = visiblePoints[stats.minIndex] ?? null;

  const activeTradeId = pinnedTradeId ?? hoveredTradeId;

  const hoveredPoint = visiblePoints.find((point) => point.trade_id === activeTradeId) ?? null;
  const hoveredIndex = hoveredPoint
    ? visiblePoints.findIndex((point) => point.trade_id === hoveredPoint.trade_id)
    : -1;
  const previousHoveredPoint =
    hoveredIndex > 0 ? visiblePoints[hoveredIndex - 1] ?? null : null;

  if (!orderedPoints.length) {
    return (
      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold">{title}</h2>
        <div className="mt-4 text-sm text-slate-500">No equity curve data available.</div>
      </div>
    );
  }

  const visibleValues = visiblePoints.map((p) => p.cumulative_pnl);
  const minValue = Math.min(...visibleValues, 0);
  const maxValue = Math.max(...visibleValues, 0);
  const range = maxValue - minValue || 1;

  const minTimestamp = visiblePoints[0]?.timestamp ?? 0;
  const maxTimestamp = visiblePoints[visiblePoints.length - 1]?.timestamp ?? minTimestamp;
  const timeRange = maxTimestamp - minTimestamp || 1;

  const xFor = (point: EnrichedEquityCurvePoint, visibleIndex: number) => {
    if (visiblePoints.length <= 1) return padding.left + chartWidth / 2;
    if (timeRange <= 0) {
      return padding.left + (visibleIndex / (visiblePoints.length - 1)) * chartWidth;
    }
    return padding.left + ((point.timestamp - minTimestamp) / timeRange) * chartWidth;
  };

  const yFor = (value: number) => {
    return padding.top + ((maxValue - value) / range) * chartHeight;
  };

  const yTicks = 5;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) => {
    return minValue + ((maxValue - minValue) / yTicks) * i;
  });

  const xTickIndexes = buildTimeTickIndexes(visiblePoints);

  const linePath = visiblePoints
    .map((point, i) => `${i === 0 ? "M" : "L"} ${xFor(point, i)} ${yFor(point.cumulative_pnl)}`)
    .join(" ");

  const areaPath = [
    linePath,
    `L ${xFor(visiblePoints[visiblePoints.length - 1], visiblePoints.length - 1)} ${height - padding.bottom}`,
    `L ${xFor(visiblePoints[0], 0)} ${height - padding.bottom}`,
    "Z",
  ].join(" ");

  const hasDrawdown =
    stats.maxDrawdown > 0 &&
    stats.drawdownPeakIndex !== null &&
    stats.drawdownTroughIndex !== null &&
    stats.drawdownPeakValue !== null &&
    stats.drawdownTroughValue !== null;

  const drawdownPeakPoint =
    stats.drawdownPeakIndex !== null ? visiblePoints[stats.drawdownPeakIndex] ?? null : null;
  const drawdownTroughPoint =
    stats.drawdownTroughIndex !== null ? visiblePoints[stats.drawdownTroughIndex] ?? null : null;

  const drawdownShadePath =
    hasDrawdown && drawdownPeakPoint && drawdownTroughPoint
      ? [
          `M ${xFor(drawdownPeakPoint, stats.drawdownPeakIndex!)} ${yFor(stats.drawdownPeakValue!)}`,
          `L ${xFor(drawdownTroughPoint, stats.drawdownTroughIndex!)} ${yFor(stats.drawdownTroughValue!)}`,
          `L ${xFor(drawdownTroughPoint, stats.drawdownTroughIndex!)} ${yFor(stats.drawdownPeakValue!)}`,
          `L ${xFor(drawdownPeakPoint, stats.drawdownPeakIndex!)} ${yFor(stats.drawdownPeakValue!)}`,
          "Z",
        ].join(" ")
      : null;

  const peakX = peakPoint ? xFor(peakPoint, stats.maxIndex) : padding.left;
  const peakY = yFor(stats.max);
  const troughX = troughPoint ? xFor(troughPoint, stats.minIndex) : padding.left;
  const troughY = yFor(stats.min);

  const peakEqualsTrough = stats.maxIndex === stats.minIndex;

  const netChangeLabel =
    stats.netChange > 0
      ? `Net change +${formatNumber(stats.netChange, 4)}`
      : stats.netChange < 0
        ? `Net change ${formatNumber(stats.netChange, 4)}`
        : `Net change ${formatNumber(stats.netChange, 4)}`;

  const zoomMode =
    zoomStartIndex === 0 && zoomEndIndex === orderedPoints.length - 1
      ? "all"
      : zoomEndIndex - zoomStartIndex + 1 <= Math.max(2, Math.ceil(orderedPoints.length * 0.25))
        ? "last25"
        : zoomEndIndex - zoomStartIndex + 1 <= Math.max(2, Math.ceil(orderedPoints.length * 0.5))
          ? "last50"
          : zoomEndIndex - zoomStartIndex + 1 <= Math.max(2, Math.ceil(orderedPoints.length * 0.75))
            ? "last75"
            : "custom";

  function applyZoomPreset(ratio: number) {
    const windowSize = Math.max(2, Math.ceil(orderedPoints.length * ratio));
    const start = Math.max(0, orderedPoints.length - windowSize);
    setZoomStartIndex(start);
    setZoomEndIndex(orderedPoints.length - 1);
    setHoveredTradeId(null);
  }

  function handleStartSlider(nextStart: number) {
    const safeStart = clamp(nextStart, 0, Math.max(orderedPoints.length - 2, 0));
    const safeEnd = Math.max(safeStart + 1, zoomEndIndex);
    setZoomStartIndex(safeStart);
    setZoomEndIndex(clamp(safeEnd, safeStart + 1, Math.max(orderedPoints.length - 1, 0)));
    setHoveredTradeId(null);
  }

  function handleEndSlider(nextEnd: number) {
    const safeEnd = clamp(nextEnd, 1, Math.max(orderedPoints.length - 1, 1));
    const safeStart = Math.min(zoomStartIndex, safeEnd - 1);
    setZoomStartIndex(clamp(safeStart, 0, safeEnd - 1));
    setZoomEndIndex(safeEnd);
    setHoveredTradeId(null);
  }

  const hoveredDelta =
    hoveredPoint && previousHoveredPoint
      ? hoveredPoint.cumulative_pnl - previousHoveredPoint.cumulative_pnl
      : hoveredPoint?.cumulative_pnl ?? null;

  const hoveredGapDays =
    hoveredPoint && previousHoveredPoint
      ? (hoveredPoint.timestamp - previousHoveredPoint.timestamp) / (1000 * 60 * 60 * 24)
      : null;

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-2xl">
          <h2 className="text-xl font-semibold">{title}</h2>
          <div className="mt-1 text-sm text-slate-500">
            Time-scale equity path ordered by trade open time and cumulative net PnL across the
            claim evidence set.
          </div>
        </div>

        <div className="grid gap-2 text-sm sm:grid-cols-3">
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">Window Start</div>
            <div className="mt-1 font-semibold">{formatNumber(stats.start, 4)}</div>
          </div>
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <div className="text-slate-500">Window End</div>
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
          label="Peak"
          value={formatNumber(stats.max, 4)}
          hint="Highest visible cumulative point"
        />
        <StatTile
          label="Trough"
          value={formatNumber(stats.min, 4)}
          hint="Lowest visible cumulative point"
        />
        <StatTile
          label="Average Trade PnL"
          value={formatNumber(stats.avgTradePnl, 4)}
          hint="Mean net PnL in current zoom window"
        />
        <StatTile
          label="Positive / Negative"
          value={`${stats.positiveTrades}/${stats.negativeTrades}`}
          hint="Visible trade count balance"
        />
      </div>

      <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-sm font-semibold text-slate-900">Zoom Window</div>
            <div className="mt-1 text-xs text-slate-500">
              True timestamp spacing with quick zoom presets and manual window controls.
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <ZoomButton
              label="All"
              active={zoomMode === "all"}
              onClick={() => {
                setZoomStartIndex(0);
                setZoomEndIndex(orderedPoints.length - 1);
                setHoveredTradeId(null);
              }}
            />
            <ZoomButton
              label="Last 75%"
              active={zoomMode === "last75"}
              onClick={() => applyZoomPreset(0.75)}
            />
            <ZoomButton
              label="Last 50%"
              active={zoomMode === "last50"}
              onClick={() => applyZoomPreset(0.5)}
            />
            <ZoomButton
              label="Last 25%"
              active={zoomMode === "last25"}
              onClick={() => applyZoomPreset(0.25)}
            />
          </div>
        </div>

        {orderedPoints.length > 2 ? (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
                <span>Window start</span>
                <span>
                  {zoomStartIndex + 1} · {formatDateShort(orderedPoints[zoomStartIndex]?.opened_at)}
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={Math.max(orderedPoints.length - 2, 0)}
                value={zoomStartIndex}
                onChange={(event) => handleStartSlider(Number(event.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
                <span>Window end</span>
                <span>
                  {zoomEndIndex + 1} · {formatDateShort(orderedPoints[zoomEndIndex]?.opened_at)}
                </span>
              </div>
              <input
                type="range"
                min={1}
                max={Math.max(orderedPoints.length - 1, 1)}
                value={zoomEndIndex}
                onChange={(event) => handleEndSlider(Number(event.target.value))}
                className="w-full"
              />
            </div>
          </div>
        ) : null}
      </div>

      <div className="mt-5 space-y-4">
        <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="h-[460px] min-w-[980px] w-full"
            onMouseLeave={() => {
              if (pinnedTradeId === null) {
                setHoveredTradeId(null);
              }
            }}
          >
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

            {xTickIndexes.map((tickIndex) => {
              const point = visiblePoints[tickIndex];
              if (!point) return null;

              const x = xFor(point, tickIndex);

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
                    y={height - padding.bottom + 20}
                    textAnchor="middle"
                    className="fill-slate-500 text-[10px]"
                  >
                    {formatDateTick(point.opened_at)}
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

            <path d={linePath} fill="none" stroke="rgba(15,23,42,0.15)" strokeWidth="6" />

            <path
              d={linePath}
              fill="none"
              stroke="#0F172A"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {hasDrawdown && drawdownPeakPoint && drawdownTroughPoint ? (
              <line
                x1={xFor(drawdownPeakPoint, stats.drawdownPeakIndex!)}
                y1={yFor(stats.drawdownPeakValue!)}
                x2={xFor(drawdownTroughPoint, stats.drawdownTroughIndex!)}
                y2={yFor(stats.drawdownTroughValue!)}
                stroke="#94A3B8"
                strokeWidth="1.5"
                strokeDasharray="4 4"
              />
            ) : null}

            {hoveredPoint && hoveredIndex >= 0 ? (
              <line
                x1={xFor(hoveredPoint, hoveredIndex)}
                y1={padding.top}
                x2={xFor(hoveredPoint, hoveredIndex)}
                y2={height - padding.bottom}
                stroke="#64748B"
                strokeWidth="1.5"
                strokeDasharray="4 4"
              />
            ) : null}

            {visiblePoints.map((point, i) => {
              const isPeak = i === stats.maxIndex;
              const isTrough = i === stats.minIndex;
              const isHovered = hoveredTradeId === point.trade_id;
              const isPinned = pinnedTradeId === point.trade_id;
              const isActive = hoveredPoint?.trade_id === point.trade_id;

              const radius = isPinned ? 8 : isActive ? 7 : isPeak || isTrough ? 6 : 4;
              const fill = isPinned
                ? "#1D4ED8"
                : isActive
                  ? "#2563EB"
                  : isPeak
                    ? "#16A34A"
                    : isTrough
                      ? "#DC2626"
                      : "#0F172A";

              return (
                <g key={`${point.trade_id}-${i}`}>
                  <circle
                    cx={xFor(point, i)}
                    cy={yFor(point.cumulative_pnl)}
                    r={radius}
                    fill={fill}
                    className="cursor-pointer"
                    onMouseEnter={() => {
                      if (pinnedTradeId === null) {
                        setHoveredTradeId(point.trade_id);
                      }
                    }}
                    onClick={() => {
                      setPinnedTradeId((current) =>
                        current === point.trade_id ? null : point.trade_id
                      );
                      setHoveredTradeId(point.trade_id);
                    }}
                  >
                    <title>
                      {`Trade #${point.trade_id} | ${point.symbol} | ${formatDateTime(
                        point.opened_at
                      )} | PnL ${point.net_pnl} | Cum ${point.cumulative_pnl}`}
                    </title>
                  </circle>

                  <circle
                    cx={xFor(point, i)}
                    cy={yFor(point.cumulative_pnl)}
                    r={14}
                    fill="transparent"
                    className="cursor-pointer"
                    onMouseEnter={() => {
                      if (pinnedTradeId === null) {
                        setHoveredTradeId(point.trade_id);
                      }
                    }}
                    onClick={() => {
                      setPinnedTradeId((current) =>
                        current === point.trade_id ? null : point.trade_id
                      );
                      setHoveredTradeId(point.trade_id);
                    }}
                  />
                </g>
              );
            })}

            {peakEqualsTrough ? (
              <text
                x={peakX + 12}
                y={peakY - 12}
                className="fill-green-600 text-[10px] font-semibold"
              >
                Peak / Trough {formatNumber(stats.max, 2)}
              </text>
            ) : (
              <>
                <text
                  x={peakX + 12}
                  y={peakY - 12}
                  className="fill-green-600 text-[10px] font-semibold"
                >
                  Peak {formatNumber(stats.max, 2)}
                </text>

                <text
                  x={troughX - 14}
                  y={troughY - 12}
                  textAnchor="end"
                  className="fill-red-700 text-[10px] font-semibold"
                >
                  Trough {formatNumber(stats.min, 2)}
                </text>
              </>
            )}

            <text
              x={width - padding.right}
              y={padding.top - 6}
              textAnchor="end"
              className="fill-slate-400 text-[10px]"
            >
              {netChangeLabel}
            </text>
          </svg>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-slate-900">Hover Analytics</div>
              <div className="mt-1 text-xs text-slate-500">
                Hover previews a point. Click a point to pin its analytics while you scroll and inspect details.
              </div>
            </div>

            {pinnedTradeId !== null ? (
              <button
                type="button"
                onClick={() => {
                  setPinnedTradeId(null);
                  setHoveredTradeId(null);
                }}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                Clear Selection
              </button>
            ) : null}
          </div>

          {hoveredPoint ? (
            <div className="mt-4 space-y-4">
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Focused point</div>
                  <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-semibold text-slate-600">
                    {pinnedTradeId !== null ? "Pinned" : "Hover"}
                  </span>
                </div>
                <div className="mt-1 text-base font-semibold text-slate-900">
                  Trade #{hoveredPoint.trade_id} · {hoveredPoint.symbol}
                </div>
                <div className="mt-2 text-sm text-slate-600">
                  {formatDateTime(hoveredPoint.opened_at)}
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Member</div>
                  <div className="mt-1 text-lg font-semibold text-slate-900">
                    {hoveredPoint.member_id}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Trade PnL</div>
                  <div className="mt-1 text-lg font-semibold text-slate-900">
                    {formatNumber(hoveredPoint.net_pnl, 4)}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Cumulative PnL
                  </div>
                  <div className="mt-1 text-lg font-semibold text-slate-900">
                    {formatNumber(hoveredPoint.cumulative_pnl, 4)}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Step Change
                  </div>
                  <div className="mt-1 text-lg font-semibold text-slate-900">
                    {hoveredDelta === null
                      ? "—"
                      : hoveredDelta > 0
                        ? `+${formatNumber(hoveredDelta, 4)}`
                        : formatNumber(hoveredDelta, 4)}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Gap From Prior
                  </div>
                  <div className="mt-1 text-lg font-semibold text-slate-900">
                    {hoveredGapDays === null ? "—" : `${formatNumber(hoveredGapDays, 2)} days`}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Sequence Position
                  </div>
                  <div className="mt-1 text-lg font-semibold text-slate-900">
                    {hoveredIndex >= 0 ? `${hoveredIndex + 1} of ${visiblePoints.length}` : "—"}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500">
              Hover a point on the chart to inspect trade ID, timestamp, PnL step change, gap from
              prior trade, and cumulative progression in the current zoom window.
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <InfoCard
          label="First point"
          value={
            <>
              Trade #{firstPoint?.trade_id} · {firstPoint?.symbol} ·{" "}
              {formatDateTime(firstPoint?.opened_at)}
            </>
          }
        />

        <InfoCard
          label="Last point"
          value={
            <>
              Trade #{lastPoint?.trade_id} · {lastPoint?.symbol} ·{" "}
              {formatDateTime(lastPoint?.opened_at)}
            </>
          }
        />

        <InfoCard
          label="Peak point"
          value={
            <>
              Trade #{peakPoint?.trade_id} · {peakPoint?.symbol} ·{" "}
              {formatDateTime(peakPoint?.opened_at)}
            </>
          }
        />

        <InfoCard
          label="Trough point"
          value={
            <>
              Trade #{troughPoint?.trade_id} · {troughPoint?.symbol} ·{" "}
              {formatDateTime(troughPoint?.opened_at)}
            </>
          }
        />
      </div>

      <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-sm font-semibold text-slate-900">Risk path note</div>
        <div className="mt-2 text-sm text-slate-600">
          This chart now uses a true time-scale axis instead of equal-spacing every point. Zoom
          controls narrow the review window, hover analytics surface trade-level context, and peak,
          trough, and drawdown remain explicitly highlighted for evidence-grade inspection.
        </div>
      </div>
    </div>
  );
}