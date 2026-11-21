# AI workflow and agent patterns cookbook

| Recipe | Use when | Code | Lesson |
| --- | --- | --- | --- |
| **Grounded answer with verified citations** | Q&A over the client's documents | `ClaudeAnswerer` + `_grounded` in [`llm.py`](../../projects/admitflow/admitflow/llm.py) | [M08 L03](../../modules/08-generative-ai-engineering/lessons/03-rag.md) |
| **Offline fallback engine** | The model must never be a single point of failure | `ExtractiveAnswerer`, `TemplateDrafter` | M08 L02 |
| **Structured output** | Code consumes the model's answer | `client.beta.messages.parse(..., output_format=Model)` in `llm.py` | [M08 L02](../../modules/08-generative-ai-engineering/lessons/02-calling-llm-apis.md) |
| **Draft-and-approve workflow** | The model proposes an action with side effects | [`assistant.py`](../../projects/admitflow/admitflow/assistant.py) + `/drafts/{id}/approve` | [M08 L05](../../modules/08-generative-ai-engineering/lessons/05-tools-and-agents.md) |
| **Manual tool-use loop** | The model needs to look things up in several steps | [`tool_loop.py`](../../modules/08-generative-ai-engineering/exercises/solutions/tool_loop.py) | M08 L05 |
| **Scoped MCP server** | Letting AI apps use your system as one user | [`mcp_server.py`](../../projects/admitflow/admitflow/mcp_server.py) | [M09 L08](../../modules/09-enterprise-integration/lessons/08-mcp.md) |
| **Evaluation in CI** | Any AI feature you'll change over time | [`evals.py`](../../projects/admitflow/admitflow/evals.py), `test_evaluation_meets_the_bar` | [M08 L06](../../modules/08-generative-ai-engineering/lessons/06-evaluation.md) |
| **Fake model client for tests** | Testing model-backed code without network or cost | `FakeClient` in [`tests/test_assistant.py`](../../projects/admitflow/tests/test_assistant.py) | M08 L02 |
| **Circuit breaker around a provider** | Provider outages shouldn't slow every request | [`circuit_breaker.py`](../../modules/10-production-security-reliability/exercises/solutions/circuit_breaker.py) | M10 L06 |
| **Data minimization before the model** | Personal data in prompts | `redact` in [`privacy.py`](../../projects/admitflow/admitflow/privacy.py) | M10 L02 |

## Rules of thumb
- Start with a single call; use a workflow when steps are known; use an agent only when the task needs the model to choose.
- Facts come from systems and documents; the model writes around them.
- The model can't do anything dangerous if no tool lets it.
- No evaluation, no launch.
