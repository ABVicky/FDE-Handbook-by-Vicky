"""Exercise 03 — reference: a manual tool-use loop, tested with a fake client (no network, no cost).

The loop follows the Messages API shape: the model returns `tool_use` blocks, we run the tool,
and send all `tool_result` blocks back in one user message, until stop_reason isn't "tool_use".
"""
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[4] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
from admitflow.models import Lead  # noqa: E402
from admitflow.rag import Retriever, load_corpus  # noqa: E402

TOOLS = [
    {"name": "search_course_info", "description": "Search current course documents; returns the top 3 sections.",
     "strict": True, "input_schema": {"type": "object", "properties": {"query": {"type": "string"}},
                                      "required": ["query"], "additionalProperties": False}},
    {"name": "get_lead", "description": "Get one lead you are allowed to see, by ID.",
     "strict": True, "input_schema": {"type": "object", "properties": {"lead_id": {"type": "string"}},
                                      "required": ["lead_id"], "additionalProperties": False}},
]


def make_tools(retriever, leads, user):
    def search_course_info(query):
        return "\n\n".join(h.chunk.text for h in retriever.search(query))

    def get_lead(lead_id):
        lead = leads.get(lead_id)
        if lead is None or lead.assigned_to not in (None, user):   # permission check in code, not in the prompt
            raise PermissionError(f"lead {lead_id} not found or not yours")
        return f"{lead.name}, interested in {lead.course}, status {lead.status}"

    return {"search_course_info": search_course_info, "get_lead": get_lead}


def run(client, question, tool_functions, model="claude-opus-5-5", max_steps=8):
    messages = [{"role": "user", "content": question}]
    for _ in range(max_steps):                       # never loop forever
        response = client.messages.create(model=model, max_tokens=16000, tools=TOOLS, messages=messages)
        if response.stop_reason != "tool_use":
            return next((b.text for b in response.content if b.type == "text"), ""), messages
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output, is_error = tool_functions[block.name](**block.input), False
            except Exception as error:               # return the error to the model instead of crashing
                output, is_error = f"Error: {error}", True
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": results})
    raise RuntimeError("too many tool steps")


class ScriptedClient:
    """Plays back a fixed sequence of model responses."""

    def __init__(self, steps):
        self.steps, self.requests = list(steps), []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        return self.steps.pop(0)


def tool_call(name, tool_input, call_id):
    return SimpleNamespace(stop_reason="tool_use",
                           content=[SimpleNamespace(type="tool_use", name=name, input=tool_input, id=call_id)])


def final(text):
    return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])


if __name__ == "__main__":
    retriever = Retriever(load_corpus(ROOT / "data" / "course_docs"))
    leads = {
        "L1": Lead("L1", datetime(2026, 9, 1), "Grace Patel", None, None, "Accounting", ["website"], assigned_to="priya"),
        "L2": Lead("L2", datetime(2026, 9, 1), "Omar Ali", None, None, "Web Development", ["ad"], assigned_to="omar"),
    }
    tools = make_tools(retriever, leads, user="priya")

    client = ScriptedClient([tool_call("search_course_info", {"query": "evening classes"}, "t1"),
                             final("Accounting and Digital Marketing have evening batches.")])
    answer, messages = run(client, "Which courses are in the evening?", tools)
    assert answer.startswith("Accounting") and "6pm to 9pm" in messages[2]["content"][0]["content"]

    client = ScriptedClient([tool_call("get_lead", {"lead_id": "L2"}, "t2"), final("I can't access that lead.")])
    answer, messages = run(client, "Tell me about lead L2", tools)
    result = messages[2]["content"][0]
    assert result["is_error"] and "not yours" in result["content"]          # permission enforced by code
    print("all checks passed")
