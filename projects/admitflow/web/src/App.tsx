import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { LeadDetailPanel } from "./components/LeadDetailPanel";
import { LeadList } from "./components/LeadList";
import { LoginForm } from "./components/LoginForm";
import type { FollowUp, Session } from "./types";

const SESSION_KEY = "admitflow.session";

function loadSession(): Session | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY); // cleared when the tab closes
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

export default function App() {
  const [session, setSession] = useState<Session | null>(loadSession);
  const [openLead, setOpenLead] = useState<string | null>(null);
  const [due, setDue] = useState<FollowUp[]>([]);

  const login = (s: Session) => {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(s));
    setSession(s);
  };
  const logout = useCallback(() => {
    sessionStorage.removeItem(SESSION_KEY);
    setSession(null);
    setOpenLead(null);
  }, []);

  useEffect(() => {
    if (session) api.dueFollowUps(session.access_token).then(setDue).catch(() => setDue([]));
  }, [session, openLead]);

  if (!session) return <LoginForm onLogin={login} />;

  return (
    <div className="app">
      <header>
        <strong>AdmitFlow</strong>
        <span className="muted">
          {session.full_name} ({session.role}) · {due.length} follow-up{due.length === 1 ? "" : "s"} due in 24h
        </span>
        <button onClick={logout}>Sign out</button>
      </header>
      <main className={openLead ? "with-detail" : ""}>
        <LeadList token={session.access_token} onOpen={setOpenLead} onAuthError={logout} />
        {openLead && <LeadDetailPanel token={session.access_token} leadId={openLead} onClose={() => setOpenLead(null)} />}
      </main>
    </div>
  );
}
