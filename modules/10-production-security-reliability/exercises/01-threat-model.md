# Exercise 01 — Threat-model AdmitFlow

1. Draw the current architecture with **trust boundaries** (internet, API, database, each third party, AI clients via MCP).
2. Apply STRIDE (Lesson 01) to: the public assistant endpoint, the webhook, the login, the outbox, and the MCP server.
3. Rate each threat by likelihood (L/M/H) and impact (L/M/H); list the existing control or the needed one.
4. Pick the **top five** and write tests for any that don't have one yet.
