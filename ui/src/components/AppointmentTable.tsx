"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, Pencil, Trash2 } from "lucide-react";
import type { Appointment } from "@/lib/types";
import { formatShortDate, formatTime } from "@/lib/format";

interface AppointmentTableProps {
  appointments: Appointment[];
  onView: (appointment: Appointment) => void;
  onEdit: (appointment: Appointment) => void;
  onDelete: (appointment: Appointment) => void;
}

type SortDirection = "asc" | "desc";

export function AppointmentTable({ appointments, onView, onEdit, onDelete }: AppointmentTableProps) {
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const sortedAppointments = useMemo(() => {
    const sorted = [...appointments].sort(
      (a, b) => new Date(a.ServiceDateTime).getTime() - new Date(b.ServiceDateTime).getTime(),
    );
    return sortDirection === "asc" ? sorted : sorted.reverse();
  }, [appointments, sortDirection]);

  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-card">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr className="border-b border-border text-text-muted">
            <th className="px-4 py-3 font-medium">
              <button
                type="button"
                onClick={() => setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"))}
                className="flex items-center gap-1 font-medium text-text-muted transition-colors hover:text-text"
              >
                Date
                {sortDirection === "asc" ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </th>
            <th className="px-4 py-3 font-medium">Time</th>
            <th className="px-4 py-3 font-medium">Client</th>
            <th className="px-4 py-3 font-medium">Service</th>
            <th className="px-4 py-3 font-medium">Address</th>
            <th className="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          {sortedAppointments.map((appointment) => (
            <tr
              key={appointment.sk}
              onClick={() => onView(appointment)}
              className="cursor-pointer border-b border-border last:border-0 transition-colors hover:bg-page-bg"
            >
              <td className="px-4 py-3">{formatShortDate(appointment.ServiceDateTime)}</td>
              <td className="px-4 py-3">{formatTime(appointment.ServiceDateTime)}</td>
              <td className="px-4 py-3">{appointment.Client.ClientName}</td>
              <td className="px-4 py-3">{appointment.Service || "—"}</td>
              <td className="px-4 py-3 text-text-muted">{appointment.Address || "—"}</td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-2">
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
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
