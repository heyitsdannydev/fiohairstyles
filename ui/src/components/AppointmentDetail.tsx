"use client";

import {
  Banknote,
  Calendar,
  CalendarCheck,
  CalendarClock,
  Car,
  CreditCard,
  ExternalLink,
  HandCoins,
  MapPin,
  MessageSquare,
  Pencil,
  Scissors,
  Wallet,
  type LucideIcon,
} from "lucide-react";
import type { Appointment } from "@/lib/types";
import { formatDateOnly, formatFullDate, formatMoney, formatTime } from "@/lib/format";

interface FieldProps {
  icon: LucideIcon;
  label: string;
  children: React.ReactNode;
}

function Field({ icon: Icon, label, children }: FieldProps) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-border bg-page-bg p-4">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
        <Icon size={18} />
      </div>
      <div>
        <p className="text-xs font-medium text-text-muted">{label}</p>
        <p className="mt-0.5 text-sm font-medium text-text">{children}</p>
      </div>
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
        <Field icon={Scissors} label="Service">
          {appointment.Service}
        </Field>
        <Field icon={CreditCard} label="Payment method">
          {appointment.PaymentMethod || "-"}
        </Field>
        <Field icon={Banknote} label="Price">
          {formatMoney(appointment.ServicePrice)}
        </Field>
        <Field icon={Car} label="Transportation">
          {formatMoney(appointment.Transportation)}
        </Field>
        <Field icon={HandCoins} label="Down payment">
          {formatMoney(appointment.DownPayment)}
        </Field>
        <Field icon={CalendarCheck} label="Down payment date">
          {appointment.DownPaymentDate ? formatDateOnly(appointment.DownPaymentDate) : "-"}
        </Field>
        <Field icon={CalendarClock} label="Remaining payment date">
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

      {appointment.CanvaProposal && (
        <div className="rounded-2xl border border-border p-4">
          <p className="flex items-center gap-1.5 text-xs font-medium text-text-muted">
            <ExternalLink size={13} />
            Canva proposal
          </p>
          <a
            href={appointment.CanvaProposal}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-1.5 block truncate text-sm text-accent underline underline-offset-2"
          >
            {appointment.CanvaProposal}
          </a>
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
