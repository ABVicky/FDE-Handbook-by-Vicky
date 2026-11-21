# Lesson 06 — Delivery and change management

**Time:** ~4 hours · **Core**

## Delivery for small, embedded teams

You don't need a heavy process. You need:
- **A visible board** (Kanban: To do / Doing / Review / Done), shared with the client
- **Short cycles:** something usable every one to two weeks, shown to real users
- **A weekly rhythm:** a status update, a 30-minute review with the sponsor, a retro with yourself or the team
- **Work in progress limits:** finish things before starting new ones

Scrum's ideas (sprints, reviews, retros) are useful even when you don't use its full ceremony.

## Estimation, honestly

From Module 04's Field Track: break work into small tasks, estimate in ranges, include invisible work (tests, reviews, deployment, training, demos), and use your own historical multiplier. Re-estimate when you learn something, and tell the client when the forecast changes.

## A risk register

Keep a simple list and review it weekly:

| Risk | Likelihood | Impact | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| SIS export format changes | M | M | Data contract; file-level checks | Mr. Okafor | Open |
| Counsellors don't adopt it | M | **H** | Per-person training; retire the spreadsheet; champion | FDE + Mr. Fernandes | Open |
| WhatsApp templates not approved before intake | M | H | Apply early; email fallback | FDE | Open |

Notice the biggest risk is human, not technical. It usually is.

## Change management: the part most projects skip

A system delivers nothing until people work differently. Plan for it as seriously as the code:

1. **Why change?** Explain the problem in users' terms ("fewer missed students, less copying").
2. **Involve users early.** Pilot users (Priya, Omar) shape the product and become champions.
3. **Remove the old way.** If the spreadsheet still exists and is still required, people will keep using it.
4. **Train per person, in their context:** short, hands-on, in their language, at the time they need it, with a one-page guide.
5. **Support visibly in the first weeks:** be present, answer quickly, fix small annoyances fast.
6. **Measure adoption** per person and per team, not just "it's live."
7. **Celebrate early wins** in the client's own channels.

The break & fix in this module is a project that skipped steps 3–6. Everything was delivered; little changed.

## Defining "done"

Agree the definition with the sponsor at the start, in layers:
- **Delivered:** features built and tested
- **Adopted:** e.g. all six counsellors active weekly, the old spreadsheet retired
- **Effective:** the outcome moved (≥ 85% contacted within 24 hours for a full intake)
- **Owned:** the client can run, support and improve it without you

An engagement isn't finished at "delivered."

## Check yourself

Do [Exercise 04](../exercises/04-risk-register.md): a risk register for AdmitFlow's next phase with at least eight risks, including at least three about people or process. Then write the definition of "done" you'd agree with Ms. Rao.

Next: [Lesson 07 — Handover and post-deployment support](07-handover.md)
