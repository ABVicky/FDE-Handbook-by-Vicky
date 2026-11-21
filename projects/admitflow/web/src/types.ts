// Shapes returned by the AdmitFlow API. Keep in sync with admitflow/api/schemas.py.

export const STATUSES = ["new", "contacted", "visit_booked", "applied", "enrolled", "lost"] as const;
export type Status = (typeof STATUSES)[number];

export interface Lead {
  lead_id: string;
  received_at: string;
  name: string;
  phone: string | null;
  email: string | null;
  course: string | null;
  sources: string[];
  status: Status;
  assigned_to: string | null;
  notes: string;
}

export interface Note {
  author: string;
  text: string;
  created_at: string;
}

export interface LeadDetail extends Lead {
  history: Note[];
}

export interface LeadPage {
  items: Lead[];
  total: number;
  page: number;
  page_size: number;
}

export interface Session {
  access_token: string;
  username: string;
  full_name: string;
  role: "counsellor" | "admin";
}

export interface FollowUp {
  followup_id: string;
  lead_id: string;
  counsellor: string;
  due: string;
  done: boolean;
}
