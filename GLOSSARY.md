# Glossary

Terms used across the handbook, with the module where each is taught.

| Term | Meaning | Module |
| --- | --- | --- |
| **Acceptance criteria** | Testable conditions a feature must meet to be "done" (Given / When / Then) | 04, 11 |
| **ADR** | Architecture Decision Record: a short note of a decision, its context, consequences and alternatives | 04 |
| **Agent** | A loop where a model chooses the next action (often tool calls) until a task is done | 08 |
| **API** | Application Programming Interface: a defined way for programs to talk to each other, often over HTTP | 02, 04 |
| **Audit log** | Append-only record of who did what, when | 10 |
| **AUC (ROC AUC)** | How well a model ranks positives above negatives (0.5 random, 1.0 perfect) | 07 |
| **Backoff** | Waiting longer between each retry (1, 2, 4… seconds) | 03, 09 |
| **Baseline** | A simple comparison point: today's metric, or a trivial model | 01, 07 |
| **BM25** | A keyword-search ranking algorithm weighting rare terms | 08 |
| **Chunk** | A piece of a document indexed for retrieval (AdmitFlow: one section) | 08 |
| **CI/CD** | Continuous integration (test every change) / continuous delivery (ship every change safely) | 06 |
| **Circuit breaker** | Stops calling a failing dependency for a while, failing fast instead | 10 |
| **Container / image** | A packaged application and its dependencies / a running instance of it | 06 |
| **CORS** | Browser rule that blocks cross-origin requests unless the server allows them | 04 |
| **Data contract** | An agreement on the format, meaning and delivery of data between two teams | 05 |
| **Dedupe** | Finding and merging records about the same thing | 03 |
| **Discovery** | Understanding a client's problem before designing a solution | 01, 11 |
| **Embedding** | A vector representing meaning, so similar texts are close together | 07, 08 |
| **Entity resolution** | Matching records about the same real-world entity across systems | 05 |
| **Error budget** | The amount of failure an SLO allows | 10 |
| **ETL / ELT** | Extract-transform-load / extract-load-transform | 05 |
| **Evaluation set** | Test cases with expected results, used to measure an AI feature | 07, 08 |
| **Field Track** | This handbook's client-facing exercise in every module | all |
| **Grounding** | Making an AI answer come only from provided sources, with citations | 08 |
| **Hallucination** | Fluent, confident output that isn't supported by facts | 08 |
| **HMAC** | A keyed hash used to sign messages (e.g. webhooks) | 09 |
| **Idempotent** | Running an operation twice has the same effect as once | 04, 05, 09 |
| **Index (database)** | A structure that makes lookups fast | 05 |
| **JWT** | JSON Web Token: a signed token carrying claims (who, role, expiry) | 04 |
| **Leakage** | Using information during training that won't exist at prediction time | 07 |
| **Least privilege** | Giving each user, service and tool only the access it needs | 06, 10 |
| **MCP** | Model Context Protocol: an open standard for exposing tools and data to AI applications | 08, 09 |
| **Migration** | A versioned script that changes a database schema | 05 |
| **N+1 problem** | Running one query per item instead of one for all | 05 |
| **OIDC** | OpenID Connect: an identity layer on OAuth 2.0 (sign-in, ID tokens) | 09 |
| **Outbox pattern** | Record intended side effects in your database; a worker delivers them | 09 |
| **PII** | Personally identifiable information | 05, 10 |
| **Precision / recall** | Of items flagged, how many were right / of right items, how many were flagged | 07 |
| **Prompt injection** | Text in the model's input that tries to override its instructions | 08, 10 |
| **RAG** | Retrieval-augmented generation: retrieve relevant documents, answer from them | 08 |
| **Rate limiting** | Restricting how often a client can call an endpoint | 10 |
| **Readiness / liveness** | "Can it serve now?" / "Is the process alive?" health checks | 06 |
| **Repository (pattern)** | Data access behind an interface, so storage can change | 04 |
| **RPO / RTO** | Maximum acceptable data loss / downtime | 10 |
| **Runbook** | Step-by-step operating procedures and alert responses | 10 |
| **SLI / SLO** | A measurement of user experience / the target for it | 10 |
| **SSO** | Single sign-on with an organization's identity provider | 09 |
| **Structured output** | A model reply constrained to a JSON schema | 08 |
| **System of record** | The authoritative source for a type of data | 09 |
| **Threat model** | A structured look at how a system could be attacked, and the controls | 10 |
| **Webhook** | An HTTP request a system sends you when something happens | 09 |
