# Exercise 03 — Add an MCP tool, safely

Add `my_followups_due(hours: int = 24)` to AdmitFlow's MCP server: the acting counsellor's open follow-ups due within the next `hours` (capped at 168), each with the lead's name and course, but no contact details.

Tests:
- returns only the acting counsellor's follow-ups
- excludes completed ones
- caps `hours`
- the tool list still contains no send/update/delete/approve tools

Then connect the server to an MCP client and ask it to plan your morning.
