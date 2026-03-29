"use client";

import { useMemo } from "react";

type Point = {
  index: number;
  cumulative_pnl: number;
};

export default function EquityCurveChart({
  title,
  points,
}: {
  title?: string;
  points: Point[];
}) {
  const width = 800;
  const height = 320;

  const padding = {
    top: 20,
    right: 20,
    bottom: 40,
    left: 60,
  };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const { scaledPoints, min, max, peakIndex, troughIndex } = useMemo(() => {
    if (!points || points.length === 0) {
      return {
        scaledPoints: [],
        min: 0,
        max: 0,
        peakIndex: -1,
        troughIndex: -1,
      };
    }

    const values = points.map((p) => p.cumulative_pnl);
    const min = Math.min(...values);
    const max = Math.max(...values);

    let peak = -Infinity;
    let peakIndex = -1;
    let troughIndex = -1;
    let maxDrawdown = 0;

    points.forEach((p, i) => {
      if (p.cumulative_pnl > peak) {
        peak = p.cumulative_pnl;
        peakIndex = i;
      }
      const dd = peak - p.cumulative_pnl;
      if (dd > maxDrawdown) {
        maxDrawdown = dd;
        troughIndex = i;
      }
    });

    const scaledPoints = points.map((p, i) => {
      const x = padding.left + (i / (points.length - 1)) * chartWidth;
      const y =
        padding.top +
        chartHeight -
        ((p.cumulative_pnl - min) / (max - min || 1)) * chartHeight;

      return { x, y, value: p.cumulative_pnl };
    });

    return { scaledPoints, min, max, peakIndex, troughIndex };
  }, [points, chartWidth, chartHeight]);

  const path = scaledPoints
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

  const yTicks = 5;
  const yStep = (max - min) / yTicks;

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      {title && <h2 className="text-xl font-semibold mb-4">{title}</h2>}

      <svg width="100%" viewBox={`0 0 ${width} ${height}`}>
        {/* GRID + Y AXIS */}
        {[...Array(yTicks + 1)].map((_, i) => {
          const value = min + i * yStep;
          const y =
            padding.top +
            chartHeight -
            ((value - min) / (max - min || 1)) * chartHeight;

          return (
            <g key={i}>
              <line
                x1={padding.left}
                x2={width - padding.right}
                y1={y}
                y2={y}
                stroke="#E2E8F0"
                strokeWidth={1}
              />
              <text
                x={padding.left - 10}
                y={y + 4}
                textAnchor="end"
                fontSize="10"
                fill="#64748B"
              >
                {value.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* X AXIS */}
        <line
          x1={padding.left}
          x2={width - padding.right}
          y1={height - padding.bottom}
          y2={height - padding.bottom}
          stroke="#94A3B8"
        />

        {/* LINE */}
        <path
          d={path}
          fill="none"
          stroke="#0F172A"
          strokeWidth={2}
        />

        {/* PEAK POINT */}
        {peakIndex >= 0 && scaledPoints[peakIndex] && (
          <circle
            cx={scaledPoints[peakIndex].x}
            cy={scaledPoints[peakIndex].y}
            r={4}
            fill="#16A34A"
          />
        )}

        {/* TROUGH POINT */}
        {troughIndex >= 0 && scaledPoints[troughIndex] && (
          <circle
            cx={scaledPoints[troughIndex].x}
            cy={scaledPoints[troughIndex].y}
            r={4}
            fill="#DC2626"
          />
        )}
      </svg>
    </div>
  );
}