import type {
  Appointment,
  AppointmentCreate,
  AppointmentUpdate,
  Client,
  ClientCreate,
  ClientUpdate,
  Service,
  ServiceCreate,
  ServiceUpdate,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

// The API/UI domains are cross-site in prod (CloudFront vs. the Lambda
// Function URL), so a session cookie would get silently dropped by
// Safari/Chrome's third-party cookie blocking. The session token instead
// travels as a plain bearer token, stored here and attached to every
// request by hand.
const SESSION_TOKEN_KEY = "SESSION_TOKEN";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(SESSION_TOKEN_KEY);
}

function setToken(token: string): void {
  window.localStorage.setItem(SESSION_TOKEN_KEY, token);
}

function clearToken(): void {
  window.localStorage.removeItem(SESSION_TOKEN_KEY);
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function redirectToLogin(): void {
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

/** Shared fetch wrapper for every authenticated endpoint except
 * login/checkSession (which handle 401 themselves). A 401 here means the
 * session expired mid-use, so it bounces straight to /login instead of
 * surfacing a raw "(401)" error on whatever page triggered it. */
async function request(path: string, init?: RequestInit): Promise<Response> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { ...authHeaders(), ...init?.headers },
  });
  if (res.status === 401) {
    clearToken();
    redirectToLogin();
  }
  return res;
}

export async function login(code: string): Promise<void> {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Code: code }),
  });
  if (!res.ok) throw new Error("Invalid code");
  const data: { Token: string } = await res.json();
  setToken(data.Token);
}

export async function logout(): Promise<void> {
  await fetch(`${API_URL}/logout`, { method: "POST", headers: authHeaders() });
  clearToken();
}

export async function checkSession(): Promise<boolean> {
  const token = getToken();
  if (!token) return false;
  const res = await fetch(`${API_URL}/session`, { headers: authHeaders() });
  if (res.status === 401) {
    clearToken();
    return false;
  }
  return res.ok;
}

export async function getClients(): Promise<Client[]> {
  const res = await request("/clients");
  if (!res.ok) throw new Error(`Failed to load clients (${res.status})`);
  const clients: Client[] = await res.json();
  // Sorted here so every consumer (the Clients page table, the Appointment
  // form's client picker) gets a consistent, alphabetical order for free.
  return clients.sort((a, b) => a.Name.localeCompare(b.Name));
}

export async function createClient(data: ClientCreate): Promise<Client> {
  const res = await request("/clients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create client (${res.status})`);
  return res.json();
}

export async function updateClient(id: string, data: ClientUpdate): Promise<Client> {
  const res = await request(`/clients/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update client (${res.status})`);
  return res.json();
}

export async function deleteClient(id: string): Promise<void> {
  const res = await request(`/clients/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to delete client (${res.status})`);
}

export async function getServices(): Promise<Service[]> {
  const res = await request("/services");
  if (!res.ok) throw new Error(`Failed to load services (${res.status})`);
  const services: Service[] = await res.json();
  return services.sort((a, b) => a.Name.localeCompare(b.Name));
}

export async function createService(data: ServiceCreate): Promise<Service> {
  const res = await request("/services", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create service (${res.status})`);
  return res.json();
}

export async function updateService(id: string, data: ServiceUpdate): Promise<Service> {
  const res = await request(`/services/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update service (${res.status})`);
  return res.json();
}

export async function deleteService(id: string): Promise<void> {
  const res = await request(`/services/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to delete service (${res.status})`);
}

export async function getAppointments(
  month: number,
  year: number,
  order: "asc" | "desc" = "desc",
  onlyFuture = false,
): Promise<Appointment[]> {
  const params = new URLSearchParams({
    month: String(month),
    year: String(year),
    order,
    only_future: String(onlyFuture),
  });
  const res = await request(`/appointments?${params}`);
  if (!res.ok) throw new Error(`Failed to load appointments (${res.status})`);
  return res.json();
}

export async function getAppointmentsIncome(
  month: number,
  year: number,
  order: "asc" | "desc" = "desc",
): Promise<Appointment[]> {
  const params = new URLSearchParams({ month: String(month), year: String(year), order });
  const res = await request(`/appointments/income?${params}`);
  if (!res.ok) throw new Error(`Failed to load income (${res.status})`);
  return res.json();
}

export async function createAppointment(data: AppointmentCreate): Promise<Appointment> {
  const res = await request("/appointments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create appointment (${res.status})`);
  return res.json();
}

export async function updateAppointment(sk: string, data: AppointmentUpdate): Promise<Appointment> {
  const res = await request(`/appointments/${encodeURIComponent(sk)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update appointment (${res.status})`);
  return res.json();
}

export async function deleteAppointment(sk: string): Promise<void> {
  const res = await request(`/appointments/${encodeURIComponent(sk)}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to delete appointment (${res.status})`);
}

export async function uploadAppointmentDocument(
  sk: string,
  label: string,
  file: File,
): Promise<Appointment> {
  const body = new FormData();
  body.append("label", label);
  body.append("file", file);
  // No Content-Type header — the browser sets the multipart boundary.
  const res = await request(`/appointments/${encodeURIComponent(sk)}/documents`, {
    method: "POST",
    body,
  });
  if (!res.ok) throw new Error(`Failed to upload document (${res.status})`);
  return res.json();
}

export async function getAppointmentDocumentUrl(sk: string, s3Path: string): Promise<string> {
  const params = new URLSearchParams({ s3_path: s3Path });
  const res = await request(
    `/appointments/${encodeURIComponent(sk)}/documents/url?${params}`,
  );
  if (!res.ok) throw new Error(`Failed to get document link (${res.status})`);
  const data: { Url: string } = await res.json();
  return data.Url;
}

export async function deleteAppointmentDocument(sk: string, s3Path: string): Promise<Appointment> {
  const params = new URLSearchParams({ s3_path: s3Path });
  const res = await request(
    `/appointments/${encodeURIComponent(sk)}/documents?${params}`,
    { method: "DELETE" },
  );
  if (!res.ok) throw new Error(`Failed to delete document (${res.status})`);
  return res.json();
}
