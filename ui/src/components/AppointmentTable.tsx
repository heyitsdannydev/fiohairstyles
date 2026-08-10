"use client";

import { useMemo } from "react";
import {
  Calendar,
  Clock,
  CreditCard,
  MapPin,
  Pencil,
  Scissors,
  Trash2,
  User,
  Wallet,
} from "lucide-react";
import type { Appointment } from "@/lib/types";
import { formatMoney, formatShortDate, formatTime } from "@/lib/format";

interface AppointmentTableProps {
  appointments: Appointment[];
  onView: (appointment: Appointment) => void;
  onEdit: (appointment: Appointment) => void;
  onDelete: (appointment: Appointment) => void;
}

interface FieldProps {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  children: React.ReactNode;
}

function Field({ icon: Icon, children }: FieldProps) {
  return (
    <p className="flex items-center gap-2 text-sm text-text-muted">
      <Icon size={15} className="shrink-0 text-text-muted" />
      {children}
    </p>
  );
}

export function AppointmentTable({ appointments, onView, onEdit, onDelete }: AppointmentTableProps) {
  const sortedAppointments = useMemo(
    () =>
      [...appointments].sort(
        (a, b) => new Date(b.ServiceDateTime).getTime() - new Date(a.ServiceDateTime).getTime(),
      ),
    [appointments],
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {sortedAppointments.map((appointment) => (
          <div
            key={appointment.sk}
            onClick={() => onView(appointment)}
            className="flex cursor-pointer flex-col gap-3 rounded-2xl border border-border bg-card p-6 shadow-sm transition-colors hover:bg-page-bg"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="flex items-center gap-2 text-base font-semibold text-text">
                  <Calendar size={16} className="text-accent" />
                  {formatShortDate(appointment.ServiceDateTime)}
                </p>
                <p className="mt-1 flex items-center gap-2 text-sm text-text-muted">
                  <Clock size={14} />
                  {formatTime(appointment.ServiceDateTime)}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onEdit(appointment);
                  }}
                  aria-label="Edit appointment"
                  className="flex items-center justify-center rounded-lg border border-border p-1.5 text-text transition-colors hover:bg-page-bg"
                >
                  <Pencil size={14} />
                </button>
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onDelete(appointment);
                  }}
                  aria-label="Delete appointment"
                  className="flex items-center justify-center rounded-lg border border-border p-1.5 text-red-600 transition-colors hover:bg-red-50"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-1.5 border-t border-border pt-3">
              <Field icon={User}>{appointment.Client.ClientName}</Field>
              <Field icon={Scissors}>{appointment.Service || "—"}</Field>
              <Field icon={MapPin}>{appointment.Address || "—"}</Field>
            </div>

            <div className="mt-1 flex items-center justify-between gap-3 rounded-xl bg-page-bg px-3 py-2">
              <span className="flex items-center gap-1.5 text-sm text-text">
                <Wallet size={15} className="text-accent" />
                {formatMoney(appointment.Total)}
              </span>
              <span className="flex items-center gap-1.5 text-sm text-text">
                <CreditCard size={15} className="text-accent" />
                {formatMoney(appointment.Total - appointment.DownPayment)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
