"use client";

import { formatMoney } from "@/lib/format";

interface IncomeOutcomeChartProps {
  income: number;
  outcome: number;
}

// Same categorical palette as OutcomesDonutChart — first two hues, kept
// fixed so "Income" and "Outcome" always read as the same colors everywhere
// in the app.
const INCOME_COLOR = "#2a78d6";
const OUTCOME_COLOR = "#eb6834";

const WIDTH = 280;
const HEIGHT = 220;
const BASELINE_Y = HEIGHT - 28;
const PLOT_HEIGHT = BASELINE_Y - 28;
const BAR_WIDTH = 72;
const BAR_RADIUS = 4;

/** A rect with rounded top corners and a square baseline, per the "4px
 * rounded data-end, square at the baseline" bar spec. */
function roundedTopBarPath(x: number, yTop: number, width: number, yBase: number): string {
  const h = yBase - yTop;
  if (h <= 0) return "";
  const r = Math.min(BAR_RADIUS, h, width / 2);
  return `M ${x} ${yBase}
    L ${x} ${yTop + r}
    Q ${x} ${yTop} ${x + r} ${yTop}
    L ${x + width - r} ${yTop}
    Q ${x + width} ${yTop} ${x + width} ${yTop + r}
    L ${x + width} ${yBase}
    Z`;
}

export function IncomeOutcomeChart({ income, outcome }: IncomeOutcomeChartProps) {
  const max = Math.max(income, outcome, 1);
  const bars = [
    { label: "Income", value: income, color: INCOME_COLOR, x: WIDTH / 2 - BAR_WIDTH - 16 },
    { label: "Outcome", value: outcome, color: OUTCOME_COLOR, x: WIDTH / 2 + 16 },
  ];

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      width="100%"
      role="img"
      aria-label={`Income ${formatMoney(income)} vs outcome ${formatMoney(outcome)}`}
      className="mx-auto max-w-xs"
    >
      {bars.map((bar) => {
        const barHeight = (bar.value / max) * PLOT_HEIGHT;
        const yTop = BASELINE_Y - barHeight;
        return (
          <g key={bar.label}>
            <path d={roundedTopBarPath(bar.x, yTop, BAR_WIDTH, BASELINE_Y)} fill={bar.color} />
            <text
              x={bar.x + BAR_WIDTH / 2}
              y={yTop - 10}
              textAnchor="middle"
              className="fill-text text-sm font-semibold"
            >
              {formatMoney(bar.value)}
            </text>
            <text
              x={bar.x + BAR_WIDTH / 2}
              y={BASELINE_Y + 20}
              textAnchor="middle"
              className="fill-text-muted text-xs"
            >
              {bar.label}
            </text>
          </g>
        );
      })}
      <line
        x1={8}
        x2={WIDTH - 8}
        y1={BASELINE_Y}
        y2={BASELINE_Y}
        stroke="var(--color-border)"
        strokeWidth={1}
      />
    </svg>
  );
}
