"use client";

import { useCallback, useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { deleteClient, getClients } from "@/lib/api";
import type { Client } from "@/lib/types";
import { PageLoader } from "@/components/PageLoader";
import { Modal } from "@/components/Modal";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { ClientForm } from "@/components/ClientForm";
import { ClientTable } from "@/components/ClientTable";

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [deletingClient, setDeletingClient] = useState<Client | null>(null);
  const [isDeleting, setDeleting] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    getClients()
      .then(setClients)
      .catch(() => setError("Could not load clients. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  async function confirmDelete() {
    if (!deletingClient) return;
    setDeleting(true);
    try {
      await deleteClient(deletingClient.sk);
      setDeletingClient(null);
      load();
    } catch {
      setError("Could not delete this client. Please try again.");
    } finally {
      setDeleting(false);
    }
  }

  const filteredClients = search.trim()
    ? clients.filter((c) => c.Name.toLowerCase().includes(search.trim().toLowerCase()))
    : clients;

  if (isLoading) {
    return <PageLoader />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight text-text">Clients</h1>
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          className="flex shrink-0 items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90"
        >
          <Plus size={16} />
          Create client
        </button>
      </div>

      {error && (
        <p className="rounded-2xl border border-border bg-card p-4 text-sm text-red-600">{error}</p>
      )}

      <input
        type="text"
        placeholder="Search by name…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-xs rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
      />

      {filteredClients.length === 0 ? (
        <p className="rounded-2xl border border-border bg-card p-6 text-sm text-text-muted">
          No clients found.
        </p>
      ) : (
        <ClientTable clients={filteredClients} onEdit={setEditingClient} onDelete={setDeletingClient} />
      )}

      {isCreateOpen && (
        <Modal title="Save client" onClose={() => setCreateOpen(false)}>
          <ClientForm
            onSaved={() => {
              setCreateOpen(false);
              load();
            }}
            onCancel={() => setCreateOpen(false)}
          />
        </Modal>
      )}

      {editingClient && (
        <Modal title="Save client" onClose={() => setEditingClient(null)}>
          <ClientForm
            client={editingClient}
            onSaved={() => {
              setEditingClient(null);
              load();
            }}
            onCancel={() => setEditingClient(null)}
          />
        </Modal>
      )}

      {deletingClient && (
        <ConfirmDialog
          title="Delete client"
          message={`Delete ${deletingClient.Name}? This cannot be undone.`}
          isConfirming={isDeleting}
          onConfirm={confirmDelete}
          onCancel={() => setDeletingClient(null)}
        />
      )}
    </div>
  );
}
