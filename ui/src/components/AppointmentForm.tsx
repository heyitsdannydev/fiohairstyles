"use client";

import { useState } from "react";
import { Calendar, MapPin, MessageSquare, Plus, Wallet } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { createAppointment, updateAppointment } from "@/lib/api";
import { Select } from "@/components/Select";
import { Modal } from "@/components/Modal";
import { ClientForm } from "@/components/ClientForm";
import { ServiceForm } from "@/components/ServiceForm";
import { ADDRESS_TYPES, PAYMENT_METHODS } from "@/lib/types";
import type { Appointment, Client, Service } from "@/lib/types";
import type { MonthYear } from "@/lib/format";

interface FormState {
  ClientId: string;
  Address: string;
  Date: string;
  Time: string;
  Service: string;
  Comments: string;
  CanvaProposal: string;
  ServicePrice: string;
  Transportation: string;
  DownPayment: string;
  PaymentMethod: string;
  DownPaymentDate: string;
  RemainingPaymentDate: string;
}

const TIME_OPTIONS = (() => {
  const pad = (n: number) => String(n).padStart(2, "0");
  const options: { label: string; value: string }[] = [];
  for (let h = 8; h <= 23; h++) {
    for (let m = 0; m < 60; m += 30) {
      if (h === 23 && m > 0) break;
      const value = `${pad(h)}:${pad(m)}`;
      const period = h < 12 ? "AM" : "PM";
      const hour12 = h % 12 === 0 ? 12 : h % 12;
      options.push({ label: `${hour12}:${pad(m)} ${period}`, value });
    }
  }
  return options;
})();

function splitDateTime(iso: string): { date: string; time: string } {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return {
    date: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`,
    time: `${pad(d.getHours())}:${pad(d.getMinutes())}`,
  };
}

function emptyForm(clients: Client[], services: Service[], defaultMonthYear?: MonthYear): FormState {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return {
    ClientId: clients[0]?.sk ?? "",
    Address: "Studio",
    Date: defaultMonthYear
      ? `${defaultMonthYear.year}-${pad(defaultMonthYear.month)}-01`
      : `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`,
    Time: TIME_OPTIONS[0].value,
    Service: services[0]?.Name ?? "",
    Comments: "",
    CanvaProposal: "",
    ServicePrice: "0",
    Transportation: "0",
    DownPayment: "0",
    PaymentMethod: PAYMENT_METHODS[0],
    DownPaymentDate: "",
    RemainingPaymentDate: "",
  };
}

function formFromAppointment(appointment: Appointment): FormState {
  const { date, time } = splitDateTime(appointment.ServiceDateTime);
  return {
    ClientId: appointment.Client.ClientId,
    Address: appointment.Address || "Studio",
    Date: date,
    Time: time,
    Service: appointment.Service,
    Comments: appointment.Comments ?? "",
    CanvaProposal: appointment.CanvaProposal ?? "",
    ServicePrice: String(appointment.ServicePrice),
    Transportation: String(appointment.Transportation),
    DownPayment: String(appointment.DownPayment),
    PaymentMethod: appointment.PaymentMethod ?? PAYMENT_METHODS[0],
    DownPaymentDate: appointment.DownPaymentDate ?? "",
    RemainingPaymentDate: appointment.RemainingPaymentDate ?? "",
  };
}

const SECTION_COLORS = {
  violet: { border: "border-l-violet-400", badge: "bg-violet-500/10 text-violet-600" },
  blue: { border: "border-l-blue-400", badge: "bg-blue-500/10 text-blue-600" },
  emerald: { border: "border-l-emerald-400", badge: "bg-emerald-500/10 text-emerald-600" },
  amber: { border: "border-l-amber-400", badge: "bg-amber-500/10 text-amber-600" },
} as const;

interface SectionProps {
  title: string;
  icon: LucideIcon;
  color: keyof typeof SECTION_COLORS;
  children: React.ReactNode;
}

function Section({ title, icon: Icon, color, children }: SectionProps) {
  const { border, badge } = SECTION_COLORS[color];
  return (
    <div className={`rounded-xl border border-border border-l-4 ${border} p-4`}>
      <div className="mb-3 flex items-center gap-2">
        <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${badge}`}>
          <Icon size={13} />
        </span>
        <p className="text-xs font-semibold tracking-wide text-text-muted uppercase">{title}</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
    </div>
  );
}

interface AppointmentFormProps {
  appointment?: Appointment;
  clients: Client[];
  services: Service[];
  defaultMonthYear?: MonthYear;
  onClientCreated: (client: Client) => void;
  onServiceCreated: (service: Service) => void;
  onSaved: () => void;
  onCancel: () => void;
}

export function AppointmentForm({
  appointment,
  clients,
  services,
  defaultMonthYear,
  onClientCreated,
  onServiceCreated,
  onSaved,
  onCancel,
}: AppointmentFormProps) {
  const isEditing = appointment !== undefined;
  const [form, setForm] = useState<FormState>(
    appointment ? formFromAppointment(appointment) : emptyForm(clients, services, defaultMonthYear),
  );
  const [addressType, setAddressType] = useState<string>(
    form.Address === "Studio" || form.Address === "" ? "Studio" : "Other",
  );
  const [isAddingClient, setAddingClient] = useState(false);
  const [isAddingService, setAddingService] = useState(false);
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleClientCreated(client: Client) {
    onClientCreated(client);
    setForm((f) => ({ ...f, ClientId: client.sk }));
    setAddingClient(false);
  }

  function handleAddressTypeChange(value: string) {
    setAddressType(value);
    setForm((f) => ({ ...f, Address: value === "Studio" ? "Studio" : "" }));
  }

  function handleServiceCreated(service: Service) {
    onServiceCreated(service);
    setForm((f) => ({ ...f, Service: service.Name }));
    setAddingService(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const client = clients.find((c) => c.sk === form.ClientId);
    if (!client) {
      setError("Please pick a client.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const serviceDateTime = `${form.Date}T${form.Time}:00`;
      const data = {
        ClientId: client.sk,
        ClientName: client.Name,
        Address: form.Address,
        ServiceDateTime: serviceDateTime,
        Service: form.Service,
        Comments: form.Comments,
        CanvaProposal: form.CanvaProposal || null,
        ServicePrice: Number(form.ServicePrice),
        Transportation: Number(form.Transportation),
        DownPayment: Number(form.DownPayment),
        PaymentMethod: form.PaymentMethod,
        DownPaymentDate: form.DownPaymentDate || null,
        RemainingPaymentDate: form.RemainingPaymentDate || null,
      };
      if (isEditing) {
        await updateAppointment(appointment.sk, data);
      } else {
        await createAppointment(data);
      }
      onSaved();
    } catch {
      setError(`Could not ${isEditing ? "update" : "save"} this appointment. Please try again.`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Section title="Client & location" icon={MapPin} color="violet">
          <div className="flex items-end gap-2 sm:col-span-2">
            <div className="flex-1">
              {clients.length === 0 ? (
                <p className="text-sm text-text-muted">No clients yet — add one first.</p>
              ) : (
                <Select
                  label="Client"
                  value={form.ClientId}
                  onChange={(value) => setForm({ ...form, ClientId: value })}
                  options={clients.map((c) => ({ label: c.Name, value: c.sk }))}
                />
              )}
            </div>
            <button
              type="button"
              onClick={() => setAddingClient(true)}
              aria-label="Add new client"
              className="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-lg border border-border text-text transition-colors hover:bg-page-bg"
            >
              <Plus size={18} />
            </button>
          </div>

          <Select
            label="Address"
            value={addressType}
            onChange={handleAddressTypeChange}
            options={ADDRESS_TYPES.map((t) => ({ label: t, value: t }))}
          />
          {addressType === "Other" && (
            <label className="flex flex-col gap-1 text-sm text-text-muted">
              Custom address
              <input
                type="text"
                value={form.Address}
                onChange={(e) => setForm({ ...form, Address: e.target.value })}
                className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
              />
            </label>
          )}
        </Section>

        <Section title="Date & service" icon={Calendar} color="blue">
          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Date
            <input
              type="date"
              required
              value={form.Date}
              onChange={(e) => setForm({ ...form, Date: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>
          <Select
            label="Time"
            value={form.Time}
            onChange={(value) => setForm({ ...form, Time: value })}
            options={TIME_OPTIONS}
          />

          <div className="flex items-end gap-2 sm:col-span-2">
            <div className="flex-1">
              {services.length === 0 ? (
                <p className="text-sm text-text-muted">No services yet — add one.</p>
              ) : (
                <Select
                  label="Service"
                  value={form.Service}
                  onChange={(value) => setForm({ ...form, Service: value })}
                  options={services.map((s) => ({ label: s.Name, value: s.Name }))}
                />
              )}
            </div>
            <button
              type="button"
              onClick={() => setAddingService(true)}
              aria-label="Add new service"
              className="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-lg border border-border text-text transition-colors hover:bg-page-bg"
            >
              <Plus size={18} />
            </button>
          </div>
        </Section>

        <Section title="Pricing & payment" icon={Wallet} color="emerald">
          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Price
            <input
              type="number"
              min="0"
              step="1"
              required
              value={form.ServicePrice}
              onChange={(e) => setForm({ ...form, ServicePrice: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Transportation
            <input
              type="number"
              min="0"
              step="1"
              required
              value={form.Transportation}
              onChange={(e) => setForm({ ...form, Transportation: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>

          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Down payment
            <input
              type="number"
              min="0"
              step="1"
              required
              value={form.DownPayment}
              onChange={(e) => setForm({ ...form, DownPayment: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>
          <Select
            label="Payment method"
            value={form.PaymentMethod}
            onChange={(value) => setForm({ ...form, PaymentMethod: value })}
            options={PAYMENT_METHODS.map((m) => ({ label: m, value: m }))}
          />

          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Down payment date
            <input
              type="date"
              value={form.DownPaymentDate}
              onChange={(e) => setForm({ ...form, DownPaymentDate: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-text-muted">
            Remaining payment date
            <input
              type="date"
              value={form.RemainingPaymentDate}
              onChange={(e) => setForm({ ...form, RemainingPaymentDate: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>
        </Section>

        <Section title="Notes" icon={MessageSquare} color="amber">
          <label className="flex flex-col gap-1 text-sm text-text-muted sm:col-span-2">
            Comments
            <textarea
              rows={3}
              value={form.Comments}
              onChange={(e) => setForm({ ...form, Comments: e.target.value })}
              className="resize-none rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-text-muted sm:col-span-2">
            Canva proposal
            <input
              type="url"
              value={form.CanvaProposal}
              onChange={(e) => setForm({ ...form, CanvaProposal: e.target.value })}
              className="rounded-lg border border-border px-3 py-2 text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </label>
        </Section>

        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

        <div className="mt-5 flex gap-2">
          <button
            type="submit"
            disabled={isSubmitting || clients.length === 0 || services.length === 0}
            className="flex-1 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {isSubmitting ? "Saving…" : "Save Appointment"}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text transition-colors hover:bg-page-bg"
          >
            Cancel
          </button>
        </div>
      </form>

      {isAddingClient && (
        <Modal title="Save client" onClose={() => setAddingClient(false)}>
          <ClientForm onSaved={handleClientCreated} onCancel={() => setAddingClient(false)} />
        </Modal>
      )}

      {isAddingService && (
        <Modal title="Save service" onClose={() => setAddingService(false)}>
          <ServiceForm onSaved={handleServiceCreated} onCancel={() => setAddingService(false)} />
        </Modal>
      )}
    </>
  );
}
