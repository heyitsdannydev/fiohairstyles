"use client";

import { useState } from "react";
import { createClient, updateClient } from "@/lib/api";
import { Select } from "@/components/Select";
import { SOURCES } from "@/lib/types";
import type { Client, SourceType } from "@/lib/types";

interface FormState {
  Name: string;
  Phone: string;
  Instagram: string;
  Source: SourceType;
}

function emptyForm(): FormState {
  return { Name: "", Phone: "", Instagram: "", Source: "Contacto" };
}

function formFromClient(client: Client): FormState {
  return {
    Name: client.Name,
    Phone: client.Phone ?? "",
    Instagram: client.Instagram ?? "",
    Source: client.Source,
  };
}

interface ClientFormProps {
  client?: Client;
  onSaved: (client: Client) => void;
  onCancel: () => void;
}

export function ClientForm({ client, onSaved, onCancel }: ClientFormProps) {
  const isEditing = client !== undefined;
  const [form, setForm] = useState<FormState>(client ? formFromClient(client) : emptyForm());
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const data = {
        Name: form.Name.trim(),
        Phone: form.Phone,
        Instagram: form.Instagram,
        Source: form.Source,
      };
      const saved = isEditing ? await updateClient(client.sk, data) : await createClient(data);
      onSaved(saved);
    } catch {
      setError(`Could not ${isEditing ? "update" : "save"} this client. Please try again.`);
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

        <label className="flex flex-col gap-1 text-sm text-text-muted">
          Phone
          <input
            type="text"
            value={form.Phone}
            onChange={(e) => setForm({ ...form, Phone: e.target.value })}
            className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
        </label>

        <label className="flex flex-col gap-1 text-sm text-text-muted">
          Instagram
          <input
            type="text"
            value={form.Instagram}
            onChange={(e) => setForm({ ...form, Instagram: e.target.value })}
            className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
        </label>

        <Select
          label="Source"
          value={form.Source}
          onChange={(value) => setForm({ ...form, Source: value as SourceType })}
          options={SOURCES.map((source) => ({ label: source, value: source }))}
        />
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
