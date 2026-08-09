export function formatMoney(value: number): string {
  return `$${Math.round(value).toLocaleString("es-UY")}`;
}

const DATE_FORMAT = new Intl.DateTimeFormat("es-UY", {
  day: "numeric",
  month: "short",
});

const FULL_DATE_FORMAT = new Intl.DateTimeFormat("es-UY", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

const TIME_FORMAT = new Intl.DateTimeFormat("es-UY", {
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

/** "2026-08-08T10:00:00" -> "8 ago". */
export function formatShortDate(iso: string): string {
  return DATE_FORMAT.format(new Date(iso));
}

/** "2026-08-08T10:00:00" -> "8 de agosto de 2026". */
export function formatFullDate(iso: string): string {
  return FULL_DATE_FORMAT.format(new Date(iso));
}

/** "2026-08-08T10:00:00" -> "10:00". */
export function formatTime(iso: string): string {
  return TIME_FORMAT.format(new Date(iso));
}

/** "2026-08-08" -> {year: 2026, month: 8, day: 8}. A bare "YYYY-MM-DD" string
 * parses as UTC midnight in `new Date()`, which can roll back a day in any
 * timezone behind UTC (Uruguay is UTC-3) — split it by hand instead of
 * constructing a Date from the raw string. */
export function parseDateOnly(value: string): { year: number; month: number; day: number } {
  const [year, month, day] = value.split("-").map(Number);
  return { year, month, day };
}

/** "2026-08-08" -> "8 ago" — safe against the UTC-parsing pitfall above. */
export function formatDateOnly(value: string): string {
  const { year, month, day } = parseDateOnly(value);
  return DATE_FORMAT.format(new Date(year, month - 1, day));
}

export interface MonthYear {
  month: number;
  year: number;
}

export function getCurrentMonthYear(): MonthYear {
  const now = new Date();
  return { month: now.getMonth() + 1, year: now.getFullYear() };
}

export function shiftMonthYear({ month, year }: MonthYear, delta: number): MonthYear {
  const date = new Date(year, month - 1 + delta, 1);
  return { month: date.getMonth() + 1, year: date.getFullYear() };
}

const MONTH_YEAR_FORMAT = new Intl.DateTimeFormat("en-US", {
  month: "long",
  year: "numeric",
});

/** {month: 8, year: 2026} -> "August 2026". */
export function formatMonthYear({ month, year }: MonthYear): string {
  return MONTH_YEAR_FORMAT.format(new Date(year, month - 1, 1));
}
