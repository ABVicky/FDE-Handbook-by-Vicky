# Exercise 04 — Model answer (excerpt)

| Risk | L | I | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Claude assistant quotes something wrong on the public site | M | H | Evaluation ≥ offline baseline before switch; fees 13/13; shadow mode for 2 weeks; instant switch back | FDE |
| Cost of public assistant spikes (bots, a viral ad) | M | M | Rate limits; provider spend limit; alert | FDE + Ms. Chen |
| Ad platform changes export format | M | M | File-level column check; data contract | FDE + marketing agency |
| Marketing agency resists channel-level reporting (it may look bad) | M | M | Involve them early; frame as optimizing, not blaming | Ms. Rao |
| Campaign names inconsistent, so reporting is meaningless | H | M | Naming convention agreed before launch | Marketing |
| Counsellors' trust drops if the assistant contradicts them | M | M | Counsellors review the FAQ document; feedback button | Mr. Fernandes |
| Key person dependency (only Priya knows the system well) | M | H | Train a second champion; recorded walkthroughs | Mr. Fernandes |
| Mr. Okafor's time unavailable for go-live checks | M | M | Book the slot now; checklist he can run alone | FDE |

**Definition of done**
- **Delivered:** campaign report and Claude engine live, all tests and evaluation bars green
- **Adopted:** Ms. Rao uses the campaign report in the monthly marketing review for two months running
- **Effective:** ad budget for the lowest-converting campaign reviewed with the agency; assistant correctness ≥ offline baseline on 50 real questions after two weeks
- **Owned:** the admissions office updates the FAQ document and re-runs the evaluation without the FDE
