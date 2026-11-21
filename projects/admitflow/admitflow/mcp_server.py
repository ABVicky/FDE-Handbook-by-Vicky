"""AdmitFlow as an MCP server (added in Module 09). Requires Python 3.10+ and `pip install mcp`.

Lets an AI assistant (Claude Desktop, an IDE, an agent) work with AdmitFlow through tools, as one
named counsellor:

    search_leads     find leads by name, email, phone or course (only ones the counsellor may see)
    get_lead         details and history of one lead
    course_info      grounded answer from the course documents, with sources
    draft_followup   create a follow-up DRAFT for a lead (status pending_approval)

There is deliberately **no tool that sends a message or changes a lead**. Approval and sending stay in
AdmitFlow, done by a person (ADR-005). Run: `admitflow mcp --user priya` (stdio transport).
"""
from __future__ import annotations

from typing import Optional


def build_server(repo=None, assistant=None, user: Optional[str] = None):
    from mcp.server.mcpserver import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError   # expected errors: clients see the message

    from .assistant import build_assistant
    from .repository import default_repository

    repo = repo or default_repository()
    assistant = assistant or build_assistant()
    counsellor = repo.get_user(user) if user else None
    if counsellor is None:
        raise SystemExit("error: --user must be an existing AdmitFlow user (set ADMITFLOW_MCP_USER)")

    def visible(lead) -> bool:
        return counsellor.role == "admin" or lead.assigned_to in (None, counsellor.username)

    server = MCPServer(
        "AdmitFlow",
        instructions=(
            "Tools for Northbridge Institute's admissions team. You act as one counsellor and can only see "
            "their leads. You can search, read and draft, but never send: drafts need human approval in AdmitFlow."
        ),
    )

    @server.tool()
    def search_leads(query: str, limit: int = 10) -> dict:
        """Search leads by name, email, phone, course or lead ID. Returns at most `limit` (max 25) matches."""
        leads, _ = repo.list_leads(search=query[:100], limit=200)
        leads = [lead for lead in leads if visible(lead)][: max(1, min(limit, 25))]
        return {"leads": [{"lead_id": l.lead_id, "name": l.name, "course": l.course, "status": l.status,
                           "channels": l.sources, "received": l.received_at.isoformat(timespec="minutes")}
                          for l in leads]}

    @server.tool()
    def get_lead(lead_id: str) -> dict:
        """Details and note history for one lead you are allowed to see."""
        lead = repo.get_lead(lead_id)
        if lead is None or not visible(lead):
            raise ToolError(f"lead {lead_id} not found")   # same message either way: don't reveal it exists
        return {"lead_id": lead.lead_id, "name": lead.name, "course": lead.course, "status": lead.status,
                "channels": lead.sources, "has_email": bool(lead.email), "has_phone": bool(lead.phone),
                "notes": [{"author": n.author, "at": n.created_at.isoformat(timespec="minutes"), "text": n.text}
                          for n in repo.notes_for(lead_id)]}

    @server.tool()
    def course_info(question: str) -> dict:
        """Answer a question from Northbridge's current course documents, with sources. May say it doesn't know."""
        if assistant is None:
            raise ToolError("course documents not available")
        answer, hits = assistant.ask(question[:500])
        return {"answer": answer.text, "answered": answer.answered, "sources": answer.citations}

    @server.tool()
    def draft_followup(lead_id: str) -> dict:
        """Create a follow-up message DRAFT for a lead. A counsellor must approve it in AdmitFlow before it's sent."""
        lead = repo.get_lead(lead_id)
        if lead is None or not visible(lead):
            raise ToolError(f"lead {lead_id} not found")
        if assistant is None:
            raise ToolError("drafting not available")
        draft = assistant.draft_followup(lead, repo.notes_for(lead_id), requested_by=counsellor.username)
        repo.save_draft(draft)
        return {"draft_id": draft.draft_id, "status": draft.status, "channel": draft.channel,
                "subject": draft.subject, "body": draft.body,
                "next_step": "Review and approve this draft in AdmitFlow; it has not been sent."}

    return server
