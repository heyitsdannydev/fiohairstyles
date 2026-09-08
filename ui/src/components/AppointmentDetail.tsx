"use client";

import { useRef, useState } from "react";
import {
  Banknote,
  Calendar,
  CalendarCheck,
  CalendarClock,
  Car,
  CreditCard,
  Download,
  ExternalLink,
  FileText,
  HandCoins,
  MapPin,
  MessageSquare,
  Paperclip,
  Pencil,
  Scissors,
  Trash2,
  Wallet,
  type LucideIcon,
} from "lucide-react";
import type { Appointment } from "@/lib/types";
import {
  deleteAppointmentDocument,
  getAppointmentDocumentUrl,
  uploadAppointmentDocument,
} from "@/lib/api";
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
  /** Called with the updated appointment after a document is added or
   * removed, so the parent can keep its state (and the list) in sync. */
  onChange?: (updated: Appointment) => void;
}

function DocumentsSection({
  appointment,
  onChange,
}: {
  appointment: Appointment;
  onChange?: (updated: Appointment) => void;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [label, setLabel] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setUploading] = useState(false);
  const [busyPath, setBusyPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const files = appointment.Files ?? [];

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const updated = await uploadAppointmentDocument(
        appointment.sk,
        label.trim() || file.name,
        file,
      );
      onChange?.(updated);
      setLabel("");
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch {
      setError("Could not upload this file. Please try again.");
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(s3Path: string) {
    setBusyPath(s3Path);
    setError(null);
    try {
      const url = await getAppointmentDocumentUrl(appointment.sk, s3Path);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch {
      setError("Could not open this document.");
    } finally {
      setBusyPath(null);
    }
  }

  async function handleDelete(s3Path: string) {
    setBusyPath(s3Path);
    setError(null);
    try {
      const updated = await deleteAppointmentDocument(appointment.sk, s3Path);
      onChange?.(updated);
    } catch {
      setError("Could not delete this document.");
    } finally {
      setBusyPath(null);
    }
  }

  return (
    <div className="rounded-2xl border border-border p-4">
      <p className="flex items-center gap-1.5 text-xs font-medium text-text-muted">
        <FileText size={13} />
        Documents
      </p>

      {files.length > 0 ? (
        <ul className="mt-2 flex flex-col gap-1.5">
          {files.map((f) => (
            <li
              key={f.S3Path}
              className="flex items-center justify-between gap-2 rounded-lg border border-border bg-page-bg px-3 py-2"
            >
              <span className="min-w-0 flex-1 truncate text-sm text-text">{f.Label}</span>
              <button
                type="button"
                onClick={() => handleDownload(f.S3Path)}
                disabled={busyPath === f.S3Path}
                aria-label={`Download ${f.Label}`}
                className="shrink-0 rounded-md p-1.5 text-text-muted transition-colors hover:bg-card hover:text-text disabled:opacity-50"
              >
                <Download size={15} />
              </button>
              <button
                type="button"
                onClick={() => handleDelete(f.S3Path)}
                disabled={busyPath === f.S3Path}
                aria-label={`Delete ${f.Label}`}
                className="shrink-0 rounded-md p-1.5 text-text-muted transition-colors hover:bg-card hover:text-red-600 disabled:opacity-50"
              >
                <Trash2 size={15} />
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-text-muted">No documents yet.</p>
      )}

      <div className="mt-3 flex flex-col gap-2">
        <input
          type="text"
          placeholder="Label (e.g. Contract)"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          className="w-full rounded-lg border border-border px-3 py-2 text-sm text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        <input
          ref={fileInputRef}
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="w-full text-sm text-text-muted file:mr-3 file:rounded-md file:border file:border-border file:bg-page-bg file:px-3 file:py-1.5 file:text-sm file:text-text hover:file:bg-card"
        />
        <button
          type="button"
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="flex items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          <Paperclip size={14} />
          {isUploading ? "Uploading…" : "Attach document"}
        </button>
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}

export function AppointmentDetail({ appointment, onEdit, onChange }: AppointmentDetailProps) {
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

      <DocumentsSection appointment={appointment} onChange={onChange} />

      <div className="flex flex-col gap-2 rounded-2xl bg-accent/10 px-4 py-3">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-2 text-sm font-medium text-text">
            <Wallet size={16} className="text-accent" />
            Total
          </span>
          <span className="text-lg font-semibold text-accent">{formatMoney(appointment.Total)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-2 text-xs font-medium text-text">
            <CreditCard size={14} className="text-accent" />
            Remaining
          </span>
          <span className="text-sm font-semibold text-accent">
            {formatMoney(appointment.Total - appointment.DownPayment)}
          </span>
        </div>
      </div>
    </div>
  );
}
