# Lesson 06 — Frontend fundamentals: HTML, CSS and React

**Time:** ~8 hours · **Core**

## Why this matters

The dashboard is what the client *sees*. To them, it *is* the product. It doesn't need to be beautiful, but it must be clear, fast, usable on a laptop and a phone, and never confusing about whether something worked.

## HTML and CSS in five minutes

HTML describes **structure and meaning**; CSS describes **appearance**.

```html
<form>
  <label>Search <input name="q" placeholder="Name, phone, email…" /></label>
  <button>Search</button>
</form>
<table>
  <thead><tr><th>Name</th><th>Course</th></tr></thead>
  <tbody><tr><td>Zoë García</td><td>Web Development</td></tr></tbody>
</table>
```

```css
table { width: 100%; border-collapse: collapse; }
td, th { padding: 8px; border-bottom: 1px solid #e5e7eb; }
@media (max-width: 900px) { main { grid-template-columns: 1fr; } }   /* responsive */
```

Use the right element (`<button>` for actions, `<label>` for inputs, `<table>` for tables). It makes the page work with keyboards and screen readers (accessibility) for free. Learn **flexbox** and **grid** for layout; see [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development).

## React: UI as a function of state

React lets you describe what the screen should look like **for the current data**, and updates the page when the data changes.

### Setup

```bash
npm create vite@latest admitflow-web -- --template react-ts
```

```bash
cd admitflow-web && npm install && npm run dev
```

### Components

A component is a function that returns markup (JSX):

```tsx
interface Lead { lead_id: string; name: string; status: string }

function LeadRow({ lead, onOpen }: { lead: Lead; onOpen: (id: string) => void }) {
  return (
    <tr onClick={() => onOpen(lead.lead_id)}>
      <td>{lead.name}</td>
      <td><span className={`badge ${lead.status}`}>{lead.status}</span></td>
    </tr>
  );
}
```

- Props (`lead`, `onOpen`) are the component's inputs. Type them with an interface.
- `{lead.name}` inserts a value. **React escapes it**, so text can't inject HTML. Never use `dangerouslySetInnerHTML` with user data.
- Use `className`, not `class`.

### State

```tsx
import { useState } from "react";

function SearchBox({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState("");
  return (
    <input value={query} onChange={(e) => { setQuery(e.target.value); onSearch(e.target.value); }} />
  );
}
```

Calling `setQuery` re-renders the component with the new value. Never modify state directly (`query = "x"` does nothing useful).

### Lists and keys

```tsx
<tbody>
  {leads.map((lead) => <LeadRow key={lead.lead_id} lead={lead} onOpen={setOpen} />)}
</tbody>
```

`key` must be a stable, unique ID, not the array index, so React can track rows correctly.

### Conditional rendering

```tsx
{loading && <p>Loading…</p>}
{error && <p role="alert" className="error">{error}</p>}
{data && data.items.length === 0 && <p>No leads match these filters.</p>}
```

Design every screen for four states: **loading, error, empty, and data**. Clients notice when an empty list looks like a broken page.

### Effects: talking to the outside world

```tsx
import { useEffect, useState } from "react";

useEffect(() => {
  let cancelled = false;
  api.leads(token, { page, search }).then((result) => {
    if (!cancelled) setData(result);
  });
  return () => { cancelled = true; };   // cleanup: ignore stale responses
}, [token, page, search]);              // re-run when these change
```

The dependency array lists every value the effect uses. The cleanup function prevents a slow, older response from overwriting a newer one.

### Forms

```tsx
function NoteForm({ onSave }: { onSave: (text: string) => Promise<void> }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: React.FormEvent) {
    event.preventDefault();          // stop the browser reloading the page
    setBusy(true);
    try { await onSave(text); setText(""); } finally { setBusy(false); }
  }
  return (
    <form onSubmit={submit}>
      <textarea value={text} onChange={(e) => setText(e.target.value)} required />
      <button disabled={busy}>{busy ? "Saving…" : "Add note"}</button>
    </form>
  );
}
```

Disable the button while saving, so double clicks don't create duplicate notes.

## Read the reference dashboard

[`projects/admitflow/web/src/`](../../../projects/admitflow/web/src/App.tsx): `App.tsx` (session and layout), `components/LoginForm.tsx`, `components/LeadList.tsx` (filters, pagination, debounced search), `components/LeadDetailPanel.tsx` (notes, status, follow-ups).

*Stretch:* **Next.js** adds routing, server rendering and API routes on top of React. State libraries (Zustand, Redux) and data-fetching libraries (TanStack Query) help in larger apps. Learn them once plain React feels comfortable.

## Check yourself

Build a `CourseFilter` component: a dropdown of courses that calls `onChange(course)` and shows "All courses" by default. Use it in your lead list. ([Exercise 03](../exercises/03-react-component.md).)

Next: [Lesson 07 — Connecting frontend and backend](07-frontend-backend.md)
