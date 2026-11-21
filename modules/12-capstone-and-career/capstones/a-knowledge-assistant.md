# Capstone A — Enterprise knowledge assistant

## The client
**Harbor Freight Logistics** (fictional): 400 staff across a head office and three warehouses. HR, safety, IT and operations policies live in ~300 documents (PDF, Word, wiki pages) on a shared drive. Some are restricted: HR investigations and salary bands (HR only), incident reports (safety team and managers), customer contracts (sales and legal).

## What they say
- **COO:** "New warehouse staff ask supervisors the same safety questions all day. Supervisors should be supervising."
- **HR lead:** "If an assistant ever shows someone the salary bands, I'm switching it off and you're fired."
- **IT:** "Everyone signs in with Microsoft Entra ID. No new passwords."
- **Warehouse supervisor:** "Half my team don't have email. They use the shared tablets and their phones."

## Your data
Create a realistic synthetic document set: at least 40 documents across 4 departments, several deliberately **restricted**, at least 3 **superseded** versions, a few scanned-looking PDFs, and some contradictions between old and new versions. Write 60+ evaluation questions, including ones a given role must **not** get answered.

## Hard requirements
- Sign-in with an OIDC identity provider (Entra ID developer tenant, or a local Keycloak standing in for it)
- **Permissions enforced at retrieval time** from document metadata/groups, tested per role
- Citations on every answer; "I don't know" with a human contact otherwise
- Works on a phone-sized screen
- Evaluation: retrieval@k, correctness, correct declines, and **zero permission leaks** on the test set, in CI

## Questions to settle in discovery
Which documents are authoritative? Who maintains them? What's the cost of a wrong safety answer? Which languages do warehouse staff use?
