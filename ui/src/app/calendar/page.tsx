"use client";

import { useCallback, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { getAppointments, getClients, getServices } from "@/lib/api";
import type { Appointment, Client, Service } from "@/lib/types";
import { PageLoader } from "@/components/PageLoader";
import { Modal } from "@/components/Modal";
import { AppointmentForm } from "@/components/AppointmentForm";
import { AppointmentDetail } from "@/components/AppointmentDetail";
import { formatMonthYear, formatTime, getCurrentMonthYear, shiftMonthYear, type MonthYear } from "@/lib/format";

const DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

/** Monday-first calendar grid for a given month, 0 = day outside the month
 * (matches Python's calendar.monthcalendar(), which the old Streamlit
 * calendar page relied on). */
function buildWeeks(year: number, month: number): number[][] {
  const daysInMonth = new Date(year, month, 0).getDate();
  const firstWeekday = (new Date(year, month - 1, 1).getDay() + 6) % 7; // Mon=0..Sun=6

  const weeks: number[][] = [];
  let week: number[] = new Array(firstWeekday).fill(0);
  for (let day = 1; day <= daysInMonth; day++) {
    week.push(day);
    if (week.length === 7) {
      weeks.push(week);
      week = [];
    }
  }
  if (week.length > 0) {
    while (week.length < 7) week.push(0);
    weeks.push(week);
  }
  return weeks;
}

export default function CalendarPage() {
  const [monthYear, setMonthYear] = useState<MonthYear>(getCurrentMonthYear());
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [isCreateOpen, setCreateOpen] = useState(false);
  const [viewingAppointment, setViewingAppointment] = useState<Appointment | null>(null);
  const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);

  const loadAppointments = useCallback((my: MonthYear) => {
    setLoading(true);
    getAppointments(my.month, my.year, "asc")
      .then(setAppointments)
      .catch(() => setError("Could not load appointments. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadAppointments(monthYear);
  }, [monthYear, loadAppointments]);

  useEffect(() => {
    getClients()
      .then(setClients)
      .catch(() => setError("Could not load clients. Is the API running?"));
  }, []);

  useEffect(() => {
    getServices()
      .then(setServices)
      .catch(() => setError("Could not load services. Is the API running?"));
  }, []);

  function handleClientCreated(client: Client) {
    setClients((prev) => [...prev, client].sort((a, b) => a.Name.localeCompare(b.Name)));
  }

  function handleServiceCreated(service: Service) {
    setServices((prev) => [...prev, service].sort((a, b) => a.Name.localeCompare(b.Name)));
  }

  const today = new Date();
  const weeks = buildWeeks(monthYear.year, monthYear.month);

  if (isLoading && appointments.length === 0) {
    return <PageLoader />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight text-text">Calendar</h1>
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

      <div className="overflow-x-auto">
        <div className="grid min-w-[720px] grid-cols-7 gap-2">
          {DAYS_OF_WEEK.map((day) => (
            <div key={day} className="px-1 text-center text-xs font-medium text-text-muted">
              {day}
            </div>
          ))}

          {weeks.flatMap((week, weekIndex) =>
            week.map((day, dayIndex) => {
              const isToday =
                day !== 0 &&
                day === today.getDate() &&
                monthYear.month === today.getMonth() + 1 &&
                monthYear.year === today.getFullYear();
              const dayAppointments =
                day === 0
                  ? []
                  : appointments.filter((a) => new Date(a.ServiceDateTime).getDate() === day);

              return (
                <div
                  key={`${weekIndex}-${dayIndex}`}
                  className={`min-h-[110px] rounded-lg border p-1.5 ${day === 0 ? "border-transparent" : "border-border bg-card"
                    }`}
                >
                  {day !== 0 && (
                    <>
                      <p
                        className={`mb-1 text-xs font-medium ${isToday ? "text-accent" : "text-text-muted"
                          }`}
                      >
                        {day}
                      </p>
                      <div className="flex flex-col gap-1">
                        {dayAppointments.map((appointment) => (
                          <button
                            key={appointment.sk}
                            type="button"
                            onClick={() => setViewingAppointment(appointment)}
                            className="truncate rounded-md bg-accent/10 px-1.5 py-1 text-left text-[11px] font-medium text-accent hover:bg-accent/20"
                            title={`${appointment.Client.ClientName} — ${formatTime(appointment.ServiceDateTime)}`}
                          >
                            {appointment.Client.ClientName} — {formatTime(appointment.ServiceDateTime)}
                          </button>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              );
            }),
          )}
        </div>
      </div>

      {isCreateOpen && (
        <Modal title="Save Appointment" onClose={() => setCreateOpen(false)}>
          <AppointmentForm
            clients={clients}
            services={services}
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

      {viewingAppointment && (
        <Modal title="Appointment detail" onClose={() => setViewingAppointment(null)}>
          <AppointmentDetail
            appointment={viewingAppointment}
            onEdit={() => {
              setEditingAppointment(viewingAppointment);
              setViewingAppointment(null);
            }}
            onChange={(updated) => {
              setViewingAppointment(updated);
              loadAppointments(monthYear);
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
              loadAppointments(monthYear);
            }}
            onCancel={() => setEditingAppointment(null)}
          />
        </Modal>
      )}
    </div>
  );
}
