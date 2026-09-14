"use client";

import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, Pencil, Trash2 } from "lucide-react";
import type { Outcome } from "@/lib/types";
import { formatDateOnly, formatMoney } from "@/lib/format";

interface OutcomeTableProps {
  outcomes: Outcome[];
  onEdit: (outcome: Outcome) => void;
  onDelete: (outcome: Outcome) => void;
}

type SortField = "date" | "amount";
type SortDirection = "asc" | "desc";

export function OutcomeTable({ outcomes, onEdit, onDelete }: OutcomeTableProps) {
  const [sortField, setSortField] = useState<SortField>("date");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  function handleSort(field: SortField) {
    if (field === sortField) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  }

  const sortedOutcomes = useMemo(() => {
    const factor = sortDirection === "asc" ? 1 : -1;
    return [...outcomes].sort((a, b) => {
      if (sortField === "amount") {
        return (a.Money - b.Money) * factor;
      }
      return a.Date.localeCompare(b.Date) * factor;
    });
  }, [outcomes, sortField, sortDirection]);

  function SortHeader({ field, label }: { field: SortField; label: string }) {
    const isActive = sortField === field;
    const Icon = sortDirection === "asc" ? ArrowUp : ArrowDown;
    return (
      <th className="px-4 py-3 font-medium">
        <button
          type="button"
          onClick={() => handleSort(field)}
          className="flex items-center gap-1 text-text-muted transition-colors hover:text-text"
        >
          {label}
          <Icon
            size={13}
            className={isActive ? "text-text" : "text-transparent"}
          />
        </button>
      </th>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-card">
      <table className="w-full min-w-[520px] text-left text-sm">
        <thead>
          <tr className="border-b border-border text-text-muted">
            <SortHeader field="date" label="Date" />
            <th className="px-4 py-3 font-medium">Product type</th>
            <SortHeader field="amount" label="Money" />
            <th className="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          {sortedOutcomes.map((outcome) => (
            <tr key={outcome.sk} className="border-b border-border last:border-0">
              <td className="px-4 py-3 whitespace-nowrap">{formatDateOnly(outcome.Date)}</td>
              <td className="px-4 py-3 font-medium">{outcome.ProductType}</td>
              <td className="px-4 py-3 whitespace-nowrap">{formatMoney(outcome.Money)}</td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(outcome)}
                    aria-label="Edit outcome"
                    className="flex items-center justify-center rounded-lg border border-border p-1.5 text-text transition-colors hover:bg-page-bg"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(outcome)}
                    aria-label="Delete outcome"
                    className="flex items-center justify-center rounded-lg border border-border p-1.5 text-red-600 transition-colors hover:bg-red-50"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
