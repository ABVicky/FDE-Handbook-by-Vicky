import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../api";
import { STATUSES, type LeadDetail, type Status } from "../types";

interface Props {
  token: string;
  leadId: string;
  onClose: () => void;
}

export function LeadDetailPanel({ token, leadId, onClose }: Props) {
  const [lead, setLead] = useState<LeadDetail | null>(null);
  const [note, setNote] = useState("");
  const [due, setDue] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLead(await api.lead(token, leadId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load lead");
    }
  }, [token, leadId]);

  useEffect(() => {
    load();
  }, [load]);

  async function run(action: () => Promise<unknown>, success: string) {
    setError(null);
    try {
      await action();
      setMessage(success);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    }
  }

  function submitNote(event: FormEvent) {
    event.preventDefault();
    run(() => api.addNote(token, leadId, note), "Note added").then(() => setNote(""));
  }

  function submitFollowUp(event: FormEvent) {
    event.preventDefault();
    run(() => api.scheduleFollowUp(token, leadId, due), "Follow-up scheduled");
  }

  if (!lead) return <aside className="card detail">{error ?? "Loading…"}</aside>;

  return (
    <aside className="card detail">
      <button className="close" onClick={onClose} aria-label="Close">×</button>
      <h2>{lead.name}</h2>
      <p className="muted">{lead.lead_id} · received {new Date(lead.received_at).toLocaleString()}</p>
      <dl>
        <dt>Phone</dt><dd>{lead.phone ? <a href={`tel:${lead.phone}`}>{lead.phone}</a> : "—"}</dd>
        <dt>Email</dt><dd>{lead.email ? <a href={`mailto:${lead.email}`}>{lead.email}</a> : "—"}</dd>
        <dt>Course</dt><dd>{lead.course ?? "—"}</dd>
        <dt>Channels</dt><dd>{lead.sources.join(", ")}</dd>
        <dt>Counsellor</dt><dd>{lead.assigned_to ?? "unassigned"}</dd>
      </dl>

      <label>
        Status
        <select
          value={lead.status}
          onChange={(e) => run(() => api.updateStatus(token, leadId, e.target.value as Status), "Status updated")}
        >
          {STATUSES.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
        </select>
      </label>

      {message && <p className="ok">{message}</p>}
      {error && <p role="alert" className="error">{error}</p>}

      <h3>History</h3>
      <ul className="history">
        {lead.history.length === 0 && <li className="muted">No notes yet.</li>}
        {lead.history.map((n, i) => (
          <li key={i}>
            <strong>{n.author}</strong> <span className="muted">{new Date(n.created_at).toLocaleString()}</span>
            {/* React escapes text automatically, so notes can't inject HTML */}
            <p>{n.text}</p>
          </li>
        ))}
      </ul>

      <form onSubmit={submitNote}>
        <textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="What happened on this call?" required />
        <button>Add note</button>
      </form>

      <form onSubmit={submitFollowUp} className="inline-form">
        <input type="datetime-local" value={due} onChange={(e) => setDue(e.target.value)} required />
        <button>Schedule follow-up</button>
      </form>
    </aside>
  );
}
