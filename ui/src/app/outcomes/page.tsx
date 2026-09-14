"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { deleteOutcome, getOutcomes, getProductTypes } from "@/lib/api";
import type { Outcome, ProductType } from "@/lib/types";
import { PageLoader } from "@/components/PageLoader";
import { Modal } from "@/components/Modal";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { OutcomeForm } from "@/components/OutcomeForm";
import { OutcomeTable } from "@/components/OutcomeTable";
import { OutcomesDonutChart, type DonutSegment } from "@/components/OutcomesDonutChart";
import {
  formatMonthYear,
  getCurrentMonthYear,
  parseDateOnly,
  shiftMonthYear,
  type MonthYear,
} from "@/lib/format";

// Fixed hue order from the categorical palette — see the dataviz skill's
// palette.md. Kept to 8 slots; beyond that, the tail folds into "Other"
// (muted gray, not a 9th generated hue).
const CATEGORICAL_PALETTE = [
  "#2a78d6",
  "#eb6834",
  "#1baf7a",
  "#eda100",
  "#e87ba4",
  "#008300",
  "#4a3aa7",
  "#e34948",
];
const OTHER_COLOR = "#898781";

function buildDonutSegments(outcomes: Outcome[]): { segments: DonutSegment[]; total: number } {
  const totals = new Map<string, number>();
  for (const outcome of outcomes) {
    totals.set(outcome.ProductType, (totals.get(outcome.ProductType) ?? 0) + outcome.Money);
  }
  const sorted = [...totals.entries()].sort((a, b) => b[1] - a[1]);
  const total = sorted.reduce((sum, [, value]) => sum + value, 0);

  if (sorted.length <= CATEGORICAL_PALETTE.length) {
    return {
      total,
      segments: sorted.map(([label, value], i) => ({ label, value, color: CATEGORICAL_PALETTE[i] })),
    };
  }

  const keep = CATEGORICAL_PALETTE.length - 1;
  const top = sorted.slice(0, keep);
  const otherTotal = sorted.slice(keep).reduce((sum, [, value]) => sum + value, 0);
  return {
    total,
    segments: [
      ...top.map(([label, value], i) => ({ label, value, color: CATEGORICAL_PALETTE[i] })),
      { label: "Other", value: otherTotal, color: OTHER_COLOR },
    ],
  };
}

export default function OutcomesPage() {
  const [monthYear, setMonthYear] = useState<MonthYear>(getCurrentMonthYear());
  const [outcomes, setOutcomes] = useState<Outcome[]>([]);
  const [productTypes, setProductTypes] = useState<ProductType[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingOutcome, setEditingOutcome] = useState<Outcome | null>(null);
  const [deletingOutcome, setDeletingOutcome] = useState<Outcome | null>(null);
  const [isDeleting, setDeleting] = useState(false);

  const loadOutcomes = useCallback(() => {
    setLoading(true);
    getOutcomes()
      .then(setOutcomes)
      .catch(() => setError("Could not load outcomes. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  const loadProductTypes = useCallback(() => {
    getProductTypes()
      .then(setProductTypes)
      .catch(() => setError("Could not load product types. Is the API running?"));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadOutcomes();
  }, [loadOutcomes]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProductTypes();
  }, [loadProductTypes]);

  function handleProductTypeCreated(productType: ProductType) {
    setProductTypes((prev) => [...prev, productType].sort((a, b) => a.Name.localeCompare(b.Name)));
  }

  async function confirmDelete() {
    if (!deletingOutcome) return;
    setDeleting(true);
    try {
      await deleteOutcome(deletingOutcome.sk);
      setDeletingOutcome(null);
      loadOutcomes();
    } catch {
      setError("Could not delete this outcome. Please try again.");
    } finally {
      setDeleting(false);
    }
  }

  const monthOutcomes = useMemo(
    () =>
      outcomes.filter((o) => {
        const { year, month } = parseDateOnly(o.Date);
        return year === monthYear.year && month === monthYear.month;
      }),
    [outcomes, monthYear],
  );

  const { segments, total } = useMemo(() => buildDonutSegments(monthOutcomes), [monthOutcomes]);

  if (isLoading) {
    return <PageLoader />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight text-text">Outcomes</h1>
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          className="flex shrink-0 items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90"
        >
          <Plus size={16} />
          Create outcome
        </button>
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

      {monthOutcomes.length === 0 ? (
        <p className="rounded-2xl border border-border bg-card p-6 text-sm text-text-muted">
          No outcomes found for {formatMonthYear(monthYear)}.
        </p>
      ) : (
        <>
          <div className="rounded-2xl border border-border bg-card p-6">
            <h2 className="mb-6 text-lg text-text-muted">
              Outcomes of {formatMonthYear(monthYear)} by product type
            </h2>
            <OutcomesDonutChart segments={segments} total={total} />
          </div>

          <OutcomeTable outcomes={monthOutcomes} onEdit={setEditingOutcome} onDelete={setDeletingOutcome} />
        </>
      )}

      {isCreateOpen && (
        <Modal title="Save outcome" onClose={() => setCreateOpen(false)}>
          <OutcomeForm
            productTypes={productTypes}
            onProductTypeCreated={handleProductTypeCreated}
            onSaved={() => {
              setCreateOpen(false);
              loadOutcomes();
            }}
            onCancel={() => setCreateOpen(false)}
          />
        </Modal>
      )}

      {editingOutcome && (
        <Modal title="Save outcome" onClose={() => setEditingOutcome(null)}>
          <OutcomeForm
            outcome={editingOutcome}
            productTypes={productTypes}
            onProductTypeCreated={handleProductTypeCreated}
            onSaved={() => {
              setEditingOutcome(null);
              loadOutcomes();
            }}
            onCancel={() => setEditingOutcome(null)}
          />
        </Modal>
      )}

      {deletingOutcome && (
        <ConfirmDialog
          title="Delete outcome"
          message={`Delete this outcome of ${deletingOutcome.ProductType}? This cannot be undone.`}
          isConfirming={isDeleting}
          onConfirm={confirmDelete}
          onCancel={() => setDeletingOutcome(null)}
        />
      )}
    </div>
  );
}
