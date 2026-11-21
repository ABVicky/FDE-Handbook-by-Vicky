// A tiny typed client for the AdmitFlow API.
// Every request goes through `request`, so auth headers and error handling live in one place.
import type { FollowUp, LeadDetail, LeadPage, Lead, Note, Session, Status } from "./types";

const BASE_URL: string = import.meta.env?.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function messageFrom(body: unknown, fallback: string): string {
  // The API always answers errors as {"error": {"status": ..., "detail": ...}}
  const detail = (body as { error?: { detail?: unknown } })?.error?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => `${d.field}: ${d.message}`).join("; ");
  if (detail && typeof detail === "object" && "message" in detail) return String((detail as { message: unknown }).message);
  return fallback;
}

export async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...options, headers: { ...headers, ...(options.headers ?? {}) } });
  } catch {
    throw new ApiError(0, "Can't reach the AdmitFlow server. Check your connection.");
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, messageFrom(body, `Request failed (${response.status})`));
  return body as T;
}

export const api = {
  login: (username: string, password: string) =>
    request<Session>("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),

  leads: (token: string, params: { page?: number; status?: Status | ""; search?: string; mine?: boolean }) => {
    const query = new URLSearchParams();
    query.set("page", String(params.page ?? 1));
    query.set("page_size", "20");
    if (params.status) query.set("status", params.status);
    if (params.search) query.set("search", params.search);
    if (params.mine) query.set("mine", "true");
    return request<LeadPage>(`/leads?${query}`, {}, token);
  },

  lead: (token: string, id: string) => request<LeadDetail>(`/leads/${encodeURIComponent(id)}`, {}, token),

  updateStatus: (token: string, id: string, status: Status) =>
    request<Lead>(`/leads/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify({ status }) }, token),

  addNote: (token: string, id: string, text: string) =>
    request<Note>(`/leads/${encodeURIComponent(id)}/notes`, { method: "POST", body: JSON.stringify({ text }) }, token),

  scheduleFollowUp: (token: string, id: string, due: string) =>
    request<FollowUp>(`/leads/${encodeURIComponent(id)}/followups`, { method: "POST", body: JSON.stringify({ due }) }, token),

  dueFollowUps: (token: string) => request<FollowUp[]>("/followups/due", {}, token),
};
