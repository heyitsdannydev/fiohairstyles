export type SourceType = "Instagram" | "Profesora" | "Contacto";

export const SOURCES: readonly SourceType[] = ["Instagram", "Profesora", "Contacto"];

export interface Client {
  pk: "Client";
  sk: string;
  Name: string;
  Instagram: string | null;
  Phone: string | null;
  Source: SourceType;
}

export interface ClientCreate {
  Name: string;
  Phone?: string | null;
  Instagram?: string | null;
  Source: SourceType;
}

export type ClientUpdate = ClientCreate;

export interface Service {
  pk: "Service";
  sk: string;
  Name: string;
}

export interface ServiceCreate {
  Name: string;
}

export type ServiceUpdate = ServiceCreate;

export interface ClientRef {
  ClientId: string;
  ClientName: string;
}

export interface Appointment {
  pk: string;
  sk: string;
  Client: ClientRef;
  Address: string | null;
  ServiceDateTime: string;
  Service: string;
  Comments: string | null;
  PaymentMethod: string | null;
  Source: SourceType | null;
  DownPaymentPercentage: number;
  ServicePrice: number;
  Transportation: number;
  // The Incomes page reads these to decide which month a payment counts
  // toward.
  DownPaymentDate: string | null;
  RemainingPaymentDate: string | null;
  Remaining: number | null;
  // Recorded by hand when it doesn't match the percentage-based estimate;
  // falls back to that estimate server-side when nothing's been recorded.
  DownPayment: number;
  Total: number;
}

export interface AppointmentCreate {
  ClientId: string;
  ClientName: string;
  Address?: string | null;
  ServiceDateTime: string;
  Service: string;
  Comments?: string | null;
  ServicePrice: number;
  Transportation: number;
  DownPaymentPercentage: number;
  PaymentMethod?: string | null;
  DownPaymentDate?: string | null;
  RemainingPaymentDate?: string | null;
}

export type AppointmentUpdate = AppointmentCreate;

// Fixed payment-method catalog, same as the old app's
// create_appointment_dialog.py — not an open catalog in the UI today.
// (Services used to be hardcoded here too — they're now managed on the
// Services page and stored in DynamoDB.)
export const PAYMENT_METHODS: readonly string[] = ["Itaú", "BROU"];

export const DOWN_PAYMENT_PERCENTAGES: readonly number[] = [0, 20, 50];

// Address is just a free-form string on the model. "Studio" is the common
// case, so the form offers it as a quick pick alongside a custom option.
export const ADDRESS_TYPES: readonly string[] = ["Studio", "Other"];
