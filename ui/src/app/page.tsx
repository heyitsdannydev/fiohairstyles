"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  CalendarDays,
  Clock3,
  MapPin,
  Plus,
  Scissors,
  type LucideIcon,
} from "lucide-react";
import { getAppointments, getClients, getServices } from "@/lib/api";
import type { Appointment, Client, Service } from "@/lib/types";
import { PageLoader } from "@/components/PageLoader";
import { Modal } from "@/components/Modal";
import { AppointmentForm } from "@/components/AppointmentForm";
import { AppointmentDetail } from "@/components/AppointmentDetail";
import { formatFullDate, formatTime, getCurrentMonthYear, shiftMonthYear } from "@/lib/format";

const UPCOMING_LIMIT = 6;
const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

function StatCard({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center gap-2 text-sm font-medium text-text-muted">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Icon size={16} />
        </span>
        {label}
      </div>
      <p className="mt-3 text-2xl font-semibold text-text">{value}</p>
    </div>
  );
}

export default function HomePage() {
  const [monthAppointments, setMonthAppointments] = useState<Appointment[]>([]);
  const [nextMonthAppointments, setNextMonthAppointments] = useState<Appointment[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [isCreateOpen, setCreateOpen] = useState(false);
  const [viewingAppointment, setViewingAppointment] = useState<Appointment | null>(null);
  const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const currentMonthYear = getCurrentMonthYear();
    const nextMonthYear = shiftMonthYear(currentMonthYear, 1);
    try {
      const [month, nextMonth, clientsData, servicesData] = await Promise.all([
        getAppointments(currentMonthYear.month, currentMonthYear.year, "asc"),
        getAppointments(nextMonthYear.month, nextMonthYear.year, "asc"),
        getClients(),
        getServices(),
      ]);
      setMonthAppointments(month);
      setNextMonthAppointments(nextMonth);
      setClients(clientsData);
      setServices(servicesData);
    } catch {
      setError("Could not load the dashboard. Is the API running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  function handleClientCreated(client: Client) {
    setClients((prev) => [...prev, client].sort((a, b) => a.Name.localeCompare(b.Name)));
  }

  function handleServiceCreated(service: Service) {
    setServices((prev) => [...prev, service].sort((a, b) => a.Name.localeCompare(b.Name)));
  }

  if (isLoading) {
    return <PageLoader />;
  }

  const now = new Date();

  const upcomingAppointments = [...monthAppointments, ...nextMonthAppointments]
    .filter((a) => new Date(a.ServiceDateTime) >= now)
    .sort((a, b) => new Date(a.ServiceDateTime).getTime() - new Date(b.ServiceDateTime).getTime());

  const weekAppointments = upcomingAppointments.filter(
    (a) => new Date(a.ServiceDateTime).getTime() - now.getTime() <= WEEK_MS,
  );

  const nextAppointments = upcomingAppointments.slice(0, UPCOMING_LIMIT);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-text">Home</h1>
          <p className="mt-1 text-sm text-text-muted">
            An overview of your upcoming appointments and business.
          </p>
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

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <StatCard icon={CalendarDays} label="Appointments this month" value={String(monthAppointments.length)} />
        <StatCard icon={Clock3} label="Next 7 days" value={String(weekAppointments.length)} />
      </div>

      <section>
        <div className="mb-4 flex items-center justify-between gap-4 border-b border-border pb-2">
          <div>
            <h2 className="text-lg font-semibold text-text">Next appointments</h2>
            <p className="text-sm text-text-muted">Your soonest appointments, coming right up.</p>
          </div>
          <Link href="/appointments" className="shrink-0 text-sm font-medium text-accent hover:opacity-80">
            View all
          </Link>
        </div>

        {nextAppointments.length === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-2xl border border-border bg-card p-10 text-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent/10 text-accent">
              <CalendarDays size={22} />
            </span>
            <p className="text-base font-semibold text-text">No appointments coming up</p>
            <p className="max-w-sm text-sm text-text-muted">
              Create a new appointment to see it show up here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {nextAppointments.map((appointment) => (
              <button
                key={appointment.sk}
                type="button"
                onClick={() => setViewingAppointment(appointment)}
                className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 text-left shadow-sm transition-colors hover:bg-page-bg"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="flex items-center gap-1.5 text-sm font-medium capitalize text-accent">
                    <CalendarDays size={14} />
                    {formatFullDate(appointment.ServiceDateTime)}
                  </span>
                  <span className="text-sm text-text-muted">{formatTime(appointment.ServiceDateTime)}</span>
                </div>
                <div>
                  <p className="text-base font-semibold text-text">{appointment.Client.ClientName}</p>
                  <p className="flex items-center gap-1.5 text-sm text-text-muted">
                    <Scissors size={13} />
                    {appointment.Service || "—"}
                  </p>
                </div>
                {appointment.Address && (
                  <p className="flex items-center gap-1.5 text-sm text-text-muted">
                    <MapPin size={13} />
                    {appointment.Address}
                  </p>
                )}
              </button>
            ))}
          </div>
        )}
      </section>

      {isCreateOpen && (
        <Modal title="Save Appointment" onClose={() => setCreateOpen(false)}>
          <AppointmentForm
            clients={clients}
            services={services}
            onClientCreated={handleClientCreated}
            onServiceCreated={handleServiceCreated}
            onSaved={() => {
              setCreateOpen(false);
              load();
            }}
            onCancel={() => setCreateOpen(false)}
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
              load();
            }}
            onCancel={() => setEditingAppointment(null)}
          />
        </Modal>
      )}
    </div>
  );
}
