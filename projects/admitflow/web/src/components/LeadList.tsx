import { useEffect, useState } from "react";
import { api, ApiError } from "../api";
import { STATUSES, type LeadPage, type Status } from "../types";

interface Props {
  token: string;
  onOpen: (leadId: string) => void;
  onAuthError: () => void;
}

export function LeadList({ token, onOpen, onAuthError }: Props) {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<Status | "">("");
  const [search, setSearch] = useState("");
  const [mine, setMine] = useState(false);
  const [data, setData] = useState<LeadPage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false; // ignore responses that arrive after the filters changed again
    setLoading(true);
    const timer = setTimeout(async () => {
      try {
        const result = await api.leads(token, { page, status, search, mine });
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return onAuthError();
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load leads");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250); // wait until the user stops typing
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [token, page, status, search, mine, onAuthError]);

  const pages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <section className="card">
      <div className="filters">
        <input
          placeholder="Search name, phone, email, course…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <select value={status} onChange={(e) => { setStatus(e.target.value as Status | ""); setPage(1); }}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s.replace("_", " ")}</option>
          ))}
        </select>
        <label className="inline">
          <input type="checkbox" checked={mine} onChange={(e) => { setMine(e.target.checked); setPage(1); }} /> Only mine
        </label>
      </div>

      {error && <p role="alert" className="error">{error}</p>}
      {loading && !data && <p>Loading…</p>}

      {data && (
        <>
          <table>
            <thead>
              <tr><th>Received</th><th>Name</th><th>Course</th><th>Channels</th><th>Status</th><th>Counsellor</th></tr>
            </thead>
            <tbody>
              {data.items.map((lead) => (
                <tr key={lead.lead_id} onClick={() => onOpen(lead.lead_id)} className="clickable">
                  <td>{new Date(lead.received_at).toLocaleDateString()}</td>
                  <td>{lead.name}</td>
                  <td>{lead.course ?? "—"}</td>
                  <td>{lead.sources.join(", ")}</td>
                  <td><span className={`badge ${lead.status}`}>{lead.status.replace("_", " ")}</span></td>
                  <td>{lead.assigned_to ?? "unassigned"}</td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr><td colSpan={6}>No leads match these filters.</td></tr>
              )}
            </tbody>
          </table>
          <div className="pager">
            <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
            <span>Page {page} of {pages} · {data.total} leads</span>
            <button disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
          </div>
        </>
      )}
    </section>
  );
}
