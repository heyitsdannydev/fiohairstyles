"use client";

import { useState } from "react";
import { createService, updateService } from "@/lib/api";
import type { Service } from "@/lib/types";

interface FormState {
  Name: string;
}

function emptyForm(): FormState {
  return { Name: "" };
}

function formFromService(service: Service): FormState {
  return { Name: service.Name };
}

interface ServiceFormProps {
  service?: Service;
  onSaved: (service: Service) => void;
  onCancel: () => void;
}

export function ServiceForm({ service, onSaved, onCancel }: ServiceFormProps) {
  const isEditing = service !== undefined;
  const [form, setForm] = useState<FormState>(service ? formFromService(service) : emptyForm());
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const data = { Name: form.Name.trim() };
      const saved = isEditing ? await updateService(service.sk, data) : await createService(data);
      onSaved(saved);
    } catch {
      setError(`Could not ${isEditing ? "update" : "save"} this service. Please try again.`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 gap-4">
        <label className="flex flex-col gap-1 text-sm text-text-muted">
          Name
          <input
            type="text"
            required
            value={form.Name}
            onChange={(e) => setForm({ ...form, Name: e.target.value })}
            className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
        </label>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      <div className="mt-5 flex gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
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
  );
}
