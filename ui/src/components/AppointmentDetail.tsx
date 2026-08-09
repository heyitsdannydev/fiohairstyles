"use client";

import { Calendar, CreditCard, MapPin, MessageSquare, Pencil, Scissors, Wallet } from "lucide-react";
import type { Appointment } from "@/lib/types";
import { formatDateOnly, formatFullDate, formatMoney, formatTime } from "@/lib/format";

interface FieldProps {
  label: string;
  children: React.ReactNode;
}

function Field({ label, children }: FieldProps) {
  return (
    <div>
      <p className="text-xs font-medium text-text-muted">{label}</p>
      <p className="mt-0.5 text-sm text-text">{children}</p>
    </div>
  );
}

interface AppointmentDetailProps {
  appointment: Appointment;
  onEdit: () => void;
}

export function AppointmentDetail({ appointment, onEdit }: AppointmentDetailProps) {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-lg font-semibold text-text">{appointment.Client.ClientName}</p>
          {appointment.Address && (
            <p className="mt-1 flex items-center gap-1.5 text-sm text-text-muted">
              <MapPin size={14} />
              {appointment.Address}
            </p>
          )}
        </div>
        <button
          type="button"
          onClick={onEdit}
          className="flex shrink-0 items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-sm text-text transition-colors hover:bg-page-bg"
        >
          <Pencil size={14} />
          Edit
        </button>
      </div>

      <div className="flex items-center gap-3 rounded-2xl border border-border bg-page-bg p-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Calendar size={18} />
        </div>
        <div>
          <p className="text-sm font-medium capitalize text-text">
            {formatFullDate(appointment.ServiceDateTime)}
          </p>
          <p className="text-xs text-text-muted">{formatTime(appointment.ServiceDateTime)}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Service">
          <span className="flex items-center gap-1.5">
            <Scissors size={13} className="text-text-muted" />
            {appointment.Service}
          </span>
        </Field>
        <Field label="Payment method">
          <span className="flex items-center gap-1.5">
            <CreditCard size={13} className="text-text-muted" />
            {appointment.PaymentMethod || "-"}
          </span>
        </Field>
        <Field label="Price">{formatMoney(appointment.ServicePrice)}</Field>
        <Field label="Transportation">{formatMoney(appointment.Transportation)}</Field>
        <Field label="Down payment %">
          {appointment.DownPaymentPercentage !== null
            ? `${appointment.DownPaymentPercentage}%`
            : "-"}
        </Field>
        <Field label="Down payment">{formatMoney(appointment.DownPayment)}</Field>
        <Field label="Down payment date">
          {appointment.DownPaymentDate ? formatDateOnly(appointment.DownPaymentDate) : "-"}
        </Field>
        <Field label="Remaining payment date">
          {appointment.RemainingPaymentDate ? formatDateOnly(appointment.RemainingPaymentDate) : "-"}
        </Field>
      </div>

      {appointment.Comments && (
        <div className="rounded-2xl border border-border p-4">
          <p className="flex items-center gap-1.5 text-xs font-medium text-text-muted">
            <MessageSquare size={13} />
            Comments
          </p>
          <p className="mt-1.5 text-sm whitespace-pre-wrap text-text">{appointment.Comments}</p>
        </div>
      )}

      <div className="flex items-center justify-between rounded-2xl bg-accent/10 px-4 py-3">
        <span className="flex items-center gap-2 text-sm font-medium text-text">
          <Wallet size={16} className="text-accent" />
          Total
        </span>
        <span className="text-lg font-semibold text-accent">{formatMoney(appointment.Total)}</span>
      </div>
    </div>
  );
}
