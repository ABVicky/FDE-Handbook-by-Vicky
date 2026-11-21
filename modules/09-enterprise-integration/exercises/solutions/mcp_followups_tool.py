"""Exercise 03 — reference: an extra MCP tool, `my_followups_due`, with its checks.

Run: python mcp_followups_tool.py   (Python 3.10+, `pip install mcp`, admitflow installed)
"""
import asyncio
import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
from admitflow.importers import import_file  # noqa: E402
from admitflow.mcp_server import build_server  # noqa: E402
from admitflow.models import User  # noqa: E402
from admitflow.repository import JsonRepository  # noqa: E402


def add_followups_tool(server, repo, username):
    @server.tool()
    def my_followups_due(hours: int = 24) -> dict:
        """Your open follow-ups due within the next `hours` (max 168), oldest first. No contact details."""
        hours = max(1, min(hours, 168))
        due = repo.followups(counsellor=username, due_before=datetime.now() + timedelta(hours=hours))
        items = []
        for followup in due:
            lead = repo.get_lead(followup.lead_id)
            items.append({"followup_id": followup.followup_id, "due": followup.due.isoformat(timespec="minutes"),
                          "lead_id": followup.lead_id, "name": lead.name if lead else "?",
                          "course": lead.course if lead else None})
        return {"hours": hours, "followups": items}


repo = JsonRepository(Path(tempfile.mkdtemp()) / "s.json")
repo.add_leads(import_file(ROOT / "data" / "leads_sample.csv", "website").leads)
repo.save_user(User("priya", "Priya", "counsellor", "x"))
now = datetime.now()
mine = repo.add_followup("ENQ-0001", "priya", now + timedelta(hours=2))
repo.add_followup("ENQ-0002", "omar", now + timedelta(hours=2))            # someone else's
done = repo.add_followup("ENQ-0003", "priya", now + timedelta(hours=3))
repo.complete_followup(done.followup_id)
repo.add_followup("ENQ-0004", "priya", now + timedelta(days=30))           # beyond any cap

server = build_server(repo, None, user="priya")
add_followups_tool(server, repo, "priya")
result = asyncio.run(server.call_tool("my_followups_due", {"hours": 9999}))
body = json.loads(result.content[0].text)
assert body["hours"] == 168
assert [f["followup_id"] for f in body["followups"]] == [mine.followup_id]
assert "email" not in json.dumps(body) and "phone" not in json.dumps(body)
names = {tool.name for tool in asyncio.run(server.list_tools())}
assert not any(word in n for n in names for word in ("send", "delete", "update", "approve"))
print(json.dumps(body, indent=2), "\nall checks passed")
