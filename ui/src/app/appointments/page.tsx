"use client";

import { useCallback, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { deleteAppointment, getAppointments, getClients, getServices } from "@/lib/api";
import type { Appointment, Client, Service } from "@/lib/types";
import { PageLoader } from "@/components/PageLoader";
import { Modal } from "@/components/Modal";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { AppointmentForm } from "@/components/AppointmentForm";
import { AppointmentTable } from "@/components/AppointmentTable";
import { AppointmentDetail } from "@/components/AppointmentDetail";
import { formatMonthYear, getCurrentMonthYear, shiftMonthYear, type MonthYear } from "@/lib/format";

export default function AppointmentsPage() {
  const [monthYear, setMonthYear] = useState<MonthYear>(getCurrentMonthYear());
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);
  const [viewingAppointment, setViewingAppointment] = useState<Appointment | null>(null);
  const [deletingAppointment, setDeletingAppointment] = useState<Appointment | null>(null);
  const [isDeleting, setDeleting] = useState(false);

  const loadAppointments = useCallback((my: MonthYear) => {
    setLoading(true);
    getAppointments(my.month, my.year, "desc")
      .then(setAppointments)
      .catch(() => setError("Could not load appointments. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  const loadClients = useCallback(() => {
    getClients()
      .then(setClients)
      .catch(() => setError("Could not load clients. Is the API running?"));
  }, []);

  const loadServices = useCallback(() => {
    getServices()
      .then(setServices)
      .catch(() => setError("Could not load services. Is the API running?"));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadAppointments(monthYear);
  }, [monthYear, loadAppointments]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadClients();
  }, [loadClients]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadServices();
  }, [loadServices]);

  function handleClientCreated(client: Client) {
    setClients((prev) => [...prev, client].sort((a, b) => a.Name.localeCompare(b.Name)));
  }

  function handleServiceCreated(service: Service) {
    setServices((prev) => [...prev, service].sort((a, b) => a.Name.localeCompare(b.Name)));
  }

  async function confirmDelete() {
    if (!deletingAppointment) return;
    setDeleting(true);
    try {
      await deleteAppointment(deletingAppointment.sk);
      setDeletingAppointment(null);
      loadAppointments(monthYear);
    } catch {
      setError("Could not delete this appointment. Please try again.");
    } finally {
      setDeleting(false);
    }
  }

  const filteredAppointments = search.trim()
    ? appointments.filter((a) =>
      a.Client.ClientName.toLowerCase().includes(search.trim().toLowerCase()),
    )
    : appointments;

  if (isLoading && appointments.length === 0) {
    return <PageLoader />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-text">Appointments</h1>
          <p className="mt-1 text-sm text-text-muted">Upcoming appointments by month.</p>
        </div>
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          className="flex shrink-0 items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90"
        >
          <Plus size={16} />
          Create Appointment
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

      <input
        type="text"
        placeholder="Search by client name…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-xs rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
      />

      {filteredAppointments.length === 0 ? (
        <p className="rounded-2xl border border-border bg-card p-6 text-sm text-text-muted">
          No appointments coming up just yet :)
        </p>
      ) : (
        <AppointmentTable
          appointments={filteredAppointments}
          onView={setViewingAppointment}
          onEdit={setEditingAppointment}
          onDelete={setDeletingAppointment}
        />
      )}

      {isCreateOpen && (
        <Modal title="Save Appointment" onClose={() => setCreateOpen(false)}>
          <AppointmentForm
            clients={clients}
            services={services}
            defaultMonthYear={monthYear}
            onClientCreated={handleClientCreated}
            onServiceCreated={handleServiceCreated}
            onSaved={() => {
              setCreateOpen(false);
              loadAppointments(monthYear);
            }}
            onCancel={() => setCreateOpen(false)}
          />
        </Modal>
      )}

      {editingAppointment && (
        <Modal title="Save Appointment" onClose={() => setEditingAppointment(null)}>
          <AppointmentForm
            appointment={editingAppointment}
            clients={clients}
            services={services}
            onClientCreated={handleClientCreated}
            onServiceCreated={handleServiceCreated}
            onSaved={() => {
              setEditingAppointment(null);
              loadAppointments(monthYear);
            }}
            onCancel={() => setEditingAppointment(null)}
          />
        </Modal>
      )}

      {viewingAppointment && (
        <Modal title="Appointment detail" onClose={() => setViewingAppointment(null)}>
          <AppointmentDetail
            appointment={viewingAppointment}
            onEdit={() => {
              setEditingAppointment(viewingAppointment);
              setViewingAppointment(null);
            }}
          />
        </Modal>
      )}

      {deletingAppointment && (
        <ConfirmDialog
          title="Delete appointment"
          message={`Delete the appointment with ${deletingAppointment.Client.ClientName}? This cannot be undone.`}
          isConfirming={isDeleting}
          onConfirm={confirmDelete}
          onCancel={() => setDeletingAppointment(null)}
        />
      )}
    </div>
  );
}
