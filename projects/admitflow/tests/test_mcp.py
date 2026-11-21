"""MCP server (Module 09). Needs Python 3.10+ and `pip install mcp`; skipped otherwise."""
import asyncio
import json
from pathlib import Path

import pytest

pytest.importorskip("mcp.server.mcpserver")
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402

from admitflow.assistant import build_assistant  # noqa: E402
from admitflow.importers import import_file  # noqa: E402
from admitflow.mcp_server import build_server  # noqa: E402
from admitflow.models import User  # noqa: E402
from admitflow.repository import JsonRepository  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def setup(tmp_path):
    repo = JsonRepository(tmp_path / "s.json")
    repo.add_leads(import_file(ROOT / "data" / "leads_sample.csv", "website").leads)
    repo.save_user(User("priya", "Priya", "counsellor", "x"))
    lead = repo.get_lead("ENQ-0002")
    lead.assigned_to = "omar"                     # someone else's lead
    repo.update_lead(lead)
    server = build_server(repo, build_assistant(str(ROOT / "data" / "course_docs")), user="priya")
    return repo, server


def call(server, name, **arguments):
    result = asyncio.run(server.call_tool(name, arguments))
    return result, (json.loads(result.content[0].text) if result.content and not result.is_error else None)


def test_tools_are_read_and_draft_only(setup):
    _, server = setup
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert names == {"search_leads", "get_lead", "course_info", "draft_followup"}
    assert not any(word in name for name in names for word in ("send", "delete", "update", "approve"))


def test_search_respects_assignment(setup):
    _, server = setup
    _, body = call(server, "search_leads", query="ENQ-000", limit=25)
    found = [item["lead_id"] for item in body["leads"]]
    assert "ENQ-0001" in found and "ENQ-0002" not in found


def test_get_lead_hides_other_counsellors_leads(setup):
    _, server = setup
    result, lead = call(server, "get_lead", lead_id="ENQ-0001")
    assert lead["name"] == "Grace Patel" and "email" not in lead          # contact details aren't exposed
    with pytest.raises(ToolError, match="not found"):       # same message as a lead that doesn't exist
        call(server, "get_lead", lead_id="ENQ-0002")
    with pytest.raises(ToolError, match="not found"):
        call(server, "draft_followup", lead_id="ENQ-0002")


def test_course_info_and_draft(setup):
    repo, server = setup
    _, info = call(server, "course_info", question="How much is Data Analytics?")
    assert info["answered"] and "1,800" in info["answer"]
    _, draft = call(server, "draft_followup", lead_id="ENQ-0001")
    assert draft["status"] == "pending_approval" and "has not been sent" in draft["next_step"]
    assert repo.get_draft(draft["draft_id"]).status == "pending_approval"


def test_unknown_user_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        build_server(JsonRepository(tmp_path / "x.json"), None, user="nobody")
