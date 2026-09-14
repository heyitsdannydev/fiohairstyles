"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { BarChart3, ChevronLeft, ChevronRight, TrendingDown, TrendingUp } from "lucide-react";
import { getAppointmentsIncome, getOutcomes } from "@/lib/api";
import type { Appointment, Outcome } from "@/lib/types";
import { PageLoader } from "@/components/PageLoader";
import { IncomeOutcomeChart } from "@/components/IncomeOutcomeChart";
import {
  formatMonthYear,
  formatMoney,
  getCurrentMonthYear,
  parseDateOnly,
  shiftMonthYear,
  type MonthYear,
} from "@/lib/format";

/** A payment counts toward whichever month its own date falls in — a down
 * payment and its remaining payment can land in different months (or the
 * same appointment can contribute to both, if paid in full the same month
 * it's booked in). "Remaining" mirrors what AppointmentDetail shows the
 * user (Total - DownPayment), not the hand-set Remaining field, which the
 * UI doesn't otherwise surface. */
function monthlyIncome(appointments: Appointment[], month: number, year: number): number {
  let total = 0;
  for (const a of appointments) {
    if (a.DownPaymentDate) {
      const parsed = parseDateOnly(a.DownPaymentDate);
      if (parsed.month === month && parsed.year === year) total += a.DownPayment;
    }
    if (a.RemainingPaymentDate) {
      const parsed = parseDateOnly(a.RemainingPaymentDate);
      if (parsed.month === month && parsed.year === year) total += a.Total - a.DownPayment;
    }
  }
  return total;
}

function monthlyOutcome(outcomes: Outcome[], month: number, year: number): number {
  return outcomes
    .filter((o) => {
      const parsed = parseDateOnly(o.Date);
      return parsed.month === month && parsed.year === year;
    })
    .reduce((sum, o) => sum + o.Money, 0);
}

function StatCard({
  icon: Icon,
  label,
  value,
  valueColor,
}: {
  icon: typeof TrendingUp;
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center gap-2 text-sm font-medium text-text-muted">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Icon size={16} />
        </span>
        {label}
      </div>
      <p className="mt-3 text-2xl font-semibold" style={valueColor ? { color: valueColor } : undefined}>
        {value}
      </p>
    </div>
  );
}

export default function ReportsPage() {
  const [monthYear, setMonthYear] = useState<MonthYear>(getCurrentMonthYear());
  const [income, setIncome] = useState(0);
  const [outcome, setOutcome] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);

  const load = useCallback((my: MonthYear) => {
    setLoading(true);
    setError(null);
    Promise.all([getAppointmentsIncome(my.month, my.year), getOutcomes()])
      .then(([appointments, outcomes]) => {
        setIncome(monthlyIncome(appointments, my.month, my.year));
        setOutcome(monthlyOutcome(outcomes, my.month, my.year));
      })
      .catch(() => setError("Could not load the report. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load(monthYear);
  }, [monthYear, load]);

  const net = useMemo(() => income - outcome, [income, outcome]);
  const netColor = net >= 0 ? "#1baf7a" : "#e34948";

  if (isLoading) {
    return <PageLoader />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text">Incomes vs Outcomes</h1>
        <p className="mt-1 text-sm text-text-muted">Income and spending by month.</p>
      </div>

      {error && (
        <p className="rounded-2xl border border-border bg-card p-4 text-sm text-red-600">{error}</p>
      )}

      <div className="mx-auto flex w-full max-w-md items-center justify-center gap-3">
        <button
          type="button"
          onClick={() => setMonthYear((prev) => shiftMonthYear(prev, -1))}
          aria-label="Previous month"
          className="rounded-lg border border-border p-2.5 text-text-muted transition-colors hover:bg-card hover:text-text"
        >
          <ChevronLeft size={22} />
        </button>
        <span className="flex min-w-[14rem] flex-1 items-center justify-center rounded-2xl border border-border bg-card px-6 py-2.5 shadow-sm">
          <span className="text-xl font-semibold tracking-tight text-text">
            {formatMonthYear(monthYear)}
          </span>
        </span>
        <button
          type="button"
          onClick={() => setMonthYear((prev) => shiftMonthYear(prev, 1))}
          aria-label="Next month"
          className="rounded-lg border border-border p-2.5 text-text-muted transition-colors hover:bg-card hover:text-text"
        >
          <ChevronRight size={22} />
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={TrendingUp} label="Income" value={formatMoney(income)} />
        <StatCard icon={TrendingDown} label="Outcome" value={formatMoney(outcome)} />
        <StatCard icon={BarChart3} label="Net" value={formatMoney(net)} valueColor={netColor} />
      </div>

      <div className="rounded-2xl border border-border bg-card p-6">
        <h2 className="mb-6 text-lg text-text-muted">
          Income vs outcome for {formatMonthYear(monthYear)}
        </h2>
        <IncomeOutcomeChart income={income} outcome={outcome} />
      </div>
    </div>
  );
}
