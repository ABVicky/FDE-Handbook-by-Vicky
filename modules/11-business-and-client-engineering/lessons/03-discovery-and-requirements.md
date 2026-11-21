# Lesson 03 — Discovery and requirements, in depth

**Time:** ~4 hours · **Core**

Module 01 introduced discovery. This lesson is the professional version: running workshops, handling conflicting stakeholders, and keeping scope under control.

## Discovery methods

| Method | Best for | Watch out for |
| --- | --- | --- |
| **One-to-one interviews** | Honest pain points, politics | People describe the official process |
| **Observation ("shadowing")** | What actually happens | Takes time; ask permission |
| **Workshops** | Shared understanding, prioritization | Loud voices dominate; prepare structure |
| **Data review** | Volumes, baselines, quality | Data reflects the old process's blind spots |
| **Artefact review** | Forms, reports, spreadsheets in use | Shadow spreadsheets reveal real needs |

Use several. Interviews tell you what people think; observation and data tell you what happens.

## Running a 90-minute discovery workshop

1. **Purpose and outcome** (5 min): "By the end we'll agree the top three problems and how we'd measure improvement."
2. **Current-state walkthrough** (25 min): draw the process together on a wall or whiteboard
3. **Pain points** (20 min): everyone adds notes silently, then groups them (silent writing stops the loudest person setting the agenda)
4. **Prioritize** (20 min): vote, then discuss impact vs effort
5. **Success measures** (15 min): for the top items, what number would show improvement?
6. **Next steps** (5 min): who, what, when

Send a one-page summary within 24 hours, and ask for corrections.

## When stakeholders disagree

Ms. Rao wants a chatbot; Mr. Fernandes wants control over his team; counsellors want less copying; Ms. Chen wants predictable cost. Don't pick a side in the room:
- **Restate each goal** in measurable terms
- Find the **shared outcome** (more students enrolled, with less effort)
- Show **trade-offs** explicitly ("the chatbot first means the team view comes in month three")
- Let the **sponsor decide**, with the trade-offs written down

## Requirements that hold up

From the [requirements template](../../../templates/requirements.md): user stories with **testable acceptance criteria**, priorities (MoSCoW: Must, Should, Could, Won't this time), non-functional requirements, and an explicit **out of scope** list.

The most important line in many requirement documents is **"Won't (this phase)"**. It's how you protect the timeline.

## Scope control and change requests

New ideas will keep arriving ("can it also send birthday wishes?"). A lightweight process:
1. Write the request down; thank the person
2. Estimate impact (effort, risk, timeline)
3. Offer options: add it and move the date; swap it for something else; put it in phase 2
4. The sponsor decides; record the decision (an ADR or a change log)

Saying yes to everything isn't helpful; it's how projects fail late. Saying no with options is.

## Working with incomplete information

Clients often don't know what they need, documentation is missing, and systems are undocumented. Habits that help:
- **State assumptions explicitly** and confirm the risky ones first
- **Build the smallest thing that tests the riskiest assumption** (a prototype with real data in week 2)
- **Keep an open-questions list** with owners and dates, visible to the client
- **Prefer reversible decisions** early

## Check yourself

Plan a 90-minute workshop with Northbridge's counsellors, reception and Mr. Fernandes about the **next phase** of AdmitFlow: agenda, materials, the exact questions you'd ask, how you'd handle Mr. Fernandes dominating, and the summary email you'd send.

Next: [Lesson 04 — Business cases and ROI](04-business-cases-and-roi.md)
