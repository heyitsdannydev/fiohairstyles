"use client";

import { useState } from "react";
import { formatMoney } from "@/lib/format";

export interface DonutSegment {
  label: string;
  value: number;
  color: string;
}

interface OutcomesDonutChartProps {
  segments: DonutSegment[];
  total: number;
}

const SIZE = 200;
const CENTER = SIZE / 2;
const RADIUS = 78;
const STROKE = 32;
const GAP_DEG = 2;

function polarToCartesian(angleDeg: number) {
  const angleRad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: CENTER + RADIUS * Math.cos(angleRad),
    y: CENTER + RADIUS * Math.sin(angleRad),
  };
}

function describeArc(startAngle: number, endAngle: number) {
  const start = polarToCartesian(endAngle);
  const end = polarToCartesian(startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${start.x} ${start.y} A ${RADIUS} ${RADIUS} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
}

export function OutcomesDonutChart({ segments, total }: OutcomesDonutChartProps) {
  const [hovered, setHovered] = useState<string | null>(null);

  let cumulative = 0;
  const arcs = segments.map((segment) => {
    const fraction = total > 0 ? segment.value / total : 0;
    const sweep = fraction * 360;
    // A single 360° segment has coincident start/end points, so the arc
    // path below degenerates to nothing — draw it as a plain circle instead.
    const isFullCircle = sweep >= 359.99;
    const halfGap = segments.length > 1 ? Math.min(GAP_DEG / 2, sweep / 2) : 0;
    const startAngle = cumulative + halfGap;
    const endAngle = Math.max(cumulative + sweep - halfGap, startAngle);
    cumulative += sweep;
    return {
      ...segment,
      fraction,
      isFullCircle,
      path: !isFullCircle && sweep > 0 ? describeArc(startAngle, endAngle) : null,
    };
  });

  return (
    <div className="flex flex-col items-center gap-8">
      <svg
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        width={SIZE}
        height={SIZE}
        className="shrink-0"
        role="img"
        aria-label={`Outcomes by product type, total ${formatMoney(total)}`}
      >
        {arcs.map((arc) => {
          if (arc.isFullCircle) {
            return (
              <circle
                key={arc.label}
                cx={CENTER}
                cy={CENTER}
                r={RADIUS}
                fill="none"
                stroke={arc.color}
                strokeWidth={hovered === arc.label ? STROKE + 6 : STROKE}
                className="cursor-pointer outline-none transition-[stroke-width] duration-150"
                tabIndex={0}
                onMouseEnter={() => setHovered(arc.label)}
                onMouseLeave={() => setHovered((h) => (h === arc.label ? null : h))}
                onFocus={() => setHovered(arc.label)}
                onBlur={() => setHovered((h) => (h === arc.label ? null : h))}
              >
                <title>
                  {arc.label}: {formatMoney(arc.value)} ({Math.round(arc.fraction * 100)}%)
                </title>
              </circle>
            );
          }
          return arc.path ? (
            <path
              key={arc.label}
              d={arc.path}
              fill="none"
              stroke={arc.color}
              strokeWidth={hovered === arc.label ? STROKE + 6 : STROKE}
              strokeLinecap="butt"
              className="cursor-pointer outline-none transition-[stroke-width] duration-150"
              tabIndex={0}
              onMouseEnter={() => setHovered(arc.label)}
              onMouseLeave={() => setHovered((h) => (h === arc.label ? null : h))}
              onFocus={() => setHovered(arc.label)}
              onBlur={() => setHovered((h) => (h === arc.label ? null : h))}
            >
              <title>
                {arc.label}: {formatMoney(arc.value)} ({Math.round(arc.fraction * 100)}%)
              </title>
            </path>
          ) : null;
        })}
        <text
          x={CENTER}
          y={CENTER - 8}
          textAnchor="middle"
          className="fill-text-muted text-[12px]"
        >
          Total
        </text>
        <text x={CENTER} y={CENTER + 16} textAnchor="middle" className="fill-text text-xl font-semibold">
          {formatMoney(total)}
        </text>
      </svg>

      <ul className="flex w-full flex-col divide-y divide-border">
        {segments.map((segment) => {
          const fraction = total > 0 ? segment.value / total : 0;
          return (
            <li
              key={segment.label}
              onMouseEnter={() => setHovered(segment.label)}
              onMouseLeave={() => setHovered((h) => (h === segment.label ? null : h))}
              className="flex items-center justify-between gap-4 py-4"
            >
              <span className="flex min-w-0 items-center gap-3">
                <span
                  className="h-3 w-3 shrink-0 rounded-full transition-transform duration-150"
                  style={{
                    backgroundColor: segment.color,
                    transform: hovered === segment.label ? "scale(1.25)" : undefined,
                  }}
                  aria-hidden="true"
                />
                <span
                  className={`truncate text-base ${hovered === segment.label ? "font-medium text-text" : "text-text"
                    }`}
                >
                  {segment.label}
                </span>
              </span>
              <span className="shrink-0 text-right text-base text-text-muted">
                {formatMoney(segment.value)} <span className="text-sm">({Math.round(fraction * 100)}%)</span>
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
