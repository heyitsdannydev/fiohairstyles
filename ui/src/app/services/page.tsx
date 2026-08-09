"use client";

import { useCallback, useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { deleteService, getServices } from "@/lib/api";
import type { Service } from "@/lib/types";
import { PageLoader } from "@/components/PageLoader";
import { Modal } from "@/components/Modal";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { ServiceForm } from "@/components/ServiceForm";
import { ServiceTable } from "@/components/ServiceTable";

export default function ServicesPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);
  const [deletingService, setDeletingService] = useState<Service | null>(null);
  const [isDeleting, setDeleting] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    getServices()
      .then(setServices)
      .catch(() => setError("Could not load services. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  async function confirmDelete() {
    if (!deletingService) return;
    setDeleting(true);
    try {
      await deleteService(deletingService.sk);
      setDeletingService(null);
      load();
    } catch {
      setError("Could not delete this service. Please try again.");
    } finally {
      setDeleting(false);
    }
  }

  if (isLoading) {
    return <PageLoader />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight text-text">Services</h1>
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          className="flex shrink-0 items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90"
        >
          <Plus size={16} />
          Create service
        </button>
      </div>

      {error && (
        <p className="rounded-2xl border border-border bg-card p-4 text-sm text-red-600">{error}</p>
      )}

      {services.length === 0 ? (
        <p className="rounded-2xl border border-border bg-card p-6 text-sm text-text-muted">
          No services found.
        </p>
      ) : (
        <ServiceTable services={services} onEdit={setEditingService} onDelete={setDeletingService} />
      )}

      {isCreateOpen && (
        <Modal title="Save service" onClose={() => setCreateOpen(false)}>
          <ServiceForm
            onSaved={() => {
              setCreateOpen(false);
              load();
            }}
            onCancel={() => setCreateOpen(false)}
          />
        </Modal>
      )}

      {editingService && (
        <Modal title="Save service" onClose={() => setEditingService(null)}>
          <ServiceForm
            service={editingService}
            onSaved={() => {
              setEditingService(null);
              load();
            }}
            onCancel={() => setEditingService(null)}
          />
        </Modal>
      )}

      {deletingService && (
        <ConfirmDialog
          title="Delete service"
          message={`Delete ${deletingService.Name}? This cannot be undone.`}
          isConfirming={isDeleting}
          onConfirm={confirmDelete}
          onCancel={() => setDeletingService(null)}
        />
      )}
    </div>
  );
}
