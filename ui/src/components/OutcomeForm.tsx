"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { createOutcome, updateOutcome } from "@/lib/api";
import { Select } from "@/components/Select";
import { Modal } from "@/components/Modal";
import { ProductTypeForm } from "@/components/ProductTypeForm";
import type { Outcome, ProductType } from "@/lib/types";

interface FormState {
  Money: string;
  Date: string;
  ProductType: string;
}

function today(): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

function emptyForm(productTypes: ProductType[]): FormState {
  return { Money: "0", Date: today(), ProductType: productTypes[0]?.Name ?? "" };
}

function formFromOutcome(outcome: Outcome): FormState {
  return { Money: String(outcome.Money), Date: outcome.Date, ProductType: outcome.ProductType };
}

interface OutcomeFormProps {
  outcome?: Outcome;
  productTypes: ProductType[];
  onProductTypeCreated: (productType: ProductType) => void;
  onSaved: (outcome: Outcome) => void;
  onCancel: () => void;
}

export function OutcomeForm({
  outcome,
  productTypes,
  onProductTypeCreated,
  onSaved,
  onCancel,
}: OutcomeFormProps) {
  const isEditing = outcome !== undefined;
  const [form, setForm] = useState<FormState>(
    outcome ? formFromOutcome(outcome) : emptyForm(productTypes),
  );
  const [isAddingProductType, setAddingProductType] = useState(false);
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleProductTypeCreated(productType: ProductType) {
    onProductTypeCreated(productType);
    setForm((f) => ({ ...f, ProductType: productType.Name }));
    setAddingProductType(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const data = {
        Money: Number(form.Money),
        Date: form.Date,
        ProductType: form.ProductType,
      };
      const saved = isEditing ? await updateOutcome(outcome.sk, data) : await createOutcome(data);
      onSaved(saved);
    } catch {
      setError(`Could not ${isEditing ? "update" : "save"} this outcome. Please try again.`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 gap-4">
          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Money
            <input
              type="number"
              min="0"
              step="1"
              required
              value={form.Money}
              onChange={(e) => setForm({ ...form, Money: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>

          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Date
            <input
              type="date"
              required
              value={form.Date}
              onChange={(e) => setForm({ ...form, Date: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>

          <div className="flex items-end gap-2">
            <div className="flex-1">
              {productTypes.length === 0 ? (
                <p className="text-sm text-text-muted">No product types yet — add one.</p>
              ) : (
                <Select
                  label="Product type"
                  value={form.ProductType}
                  onChange={(value) => setForm({ ...form, ProductType: value })}
                  options={productTypes.map((p) => ({ label: p.Name, value: p.Name }))}
                />
              )}
            </div>
            <button
              type="button"
              onClick={() => setAddingProductType(true)}
              aria-label="Add new product type"
              className="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-lg border border-border text-text transition-colors hover:bg-page-bg"
            >
              <Plus size={18} />
            </button>
          </div>
        </div>

        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

        <div className="mt-5 flex gap-2">
          <button
            type="submit"
            disabled={isSubmitting || productTypes.length === 0}
            className="flex-1 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {isSubmitting ? "Saving…" : "Save"}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text transition-colors hover:bg-page-bg"
          >
            Cancel
          </button>
        </div>
      </form>

      {isAddingProductType && (
        <Modal title="Save product type" onClose={() => setAddingProductType(false)}>
          <ProductTypeForm
            onSaved={handleProductTypeCreated}
            onCancel={() => setAddingProductType(false)}
          />
        </Modal>
      )}
    </>
  );
}
