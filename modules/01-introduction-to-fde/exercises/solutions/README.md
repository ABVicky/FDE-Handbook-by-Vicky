# Module 01 — Solutions

These are *model* answers. Yours can differ and still be right, as long as the reasoning holds.

---

## Lesson 03 check yourself

1. Solutions engineer: built a pre-sale demo to win the deal.
2. FDE: production pipeline plus alerting, in the customer's context.
3. Technical PM: deciding product priorities.
4. AI / ML engineer: model quality work on the product.

---

## Exercise 01 — Classify the role

1. **FDE**: integration inside the customer's environment plus user training.
2. **Solutions engineer**: pre-sale demo and security questions.
3. **Implementation consultant**: configuring existing software to a spec.
4. **AI engineer** (or software engineer): product-wide model improvement, no specific customer.
5. **Technical PM**: customer research feeding a product spec.
6. **FDE**: adapted to customer constraints, deployed, measured business outcome.
7. **Software engineer**: internal product code quality.
8. **FDE**: handover plus feeding reusable work back to the product.

**Bonus:** #1 could also be a strong implementation consultant if no custom code was involved. #4 depends on whether "ranking model" work is ML (AI engineer) or systems optimization (software engineer). Role boundaries blur in real companies.

---

## Exercise 02 — Sample answer for B (hospital policy assistant)

| Problem | Why the tool alone can't solve it | Engineering work needed |
| --- | --- | --- |
| 2,000 files in mixed formats | The tool needs clean, parsed text | Ingestion pipeline: parse PDF/Word, extract text and metadata |
| Outdated policies mixed with current ones | The assistant may quote obsolete rules | Version detection, effective-date metadata, filtering to current versions |
| Some policies restricted to senior staff | The assistant could leak restricted content | Connect to hospital identity (SSO); enforce document-level permissions at retrieval |
| Staff need to trust answers | Clinical and legal risk | Citations to source documents; "I don't know" behaviour; evaluation on real questions |
| Hospital IT rules on data | Data may not be allowed to leave its network | Deployment within approved environment; security review |
| Staff work on shared terminals and phones | Adoption depends on fitting the workflow | Integrate into the intranet or messaging tool staff already use |

**Tackle first:** permissions and outdated documents. A wrong or leaked answer destroys trust before anything else matters.

---

## Exercise 04 — Spot the bad problem statement

**1. "We need an AI chatbot for our website."**
*Wrong:* names a solution; no who, no cost, no success metric.
*Ask:* What do visitors need that they can't get today? What happens to enquiries now? What does a lost enquiry cost?
*Rewrite:* "Prospective students who enquire through the website outside office hours (≈ 35% of enquiries, *assumption*) wait an average of 18 hours for a reply, and about half never hear back. We'll consider this solved when 90% of enquiries get an accurate answer or a booked call within 1 hour, without adding staff."

**2. "Our processes are inefficient…"**
*Wrong:* vague; no specific process, user or measure.
*Ask:* Which process costs the most time or money? Who does it? How often?
*Rewrite:* pick one concrete process, e.g. "Finance staff spend ~25 hours a week re-typing supplier invoices into the ERP…", with baseline and target.

**3. "Customer support is slow."**
*Wrong:* no measure, no baseline, no cause.
*Ask:* Slow how: first response, resolution time? For which request types? What's the baseline?
*Rewrite:* "Median first response time for 'where is my order' tickets (60% of volume) is 9 hours. Target: under 30 minutes within 3 months, with customer-satisfaction score unchanged or better."

**4. "Build a dashboard showing all the data…"**
*Wrong:* names a solution; "all the data" is unbounded scope; "better decisions" isn't measurable.
*Ask:* Which decisions? Made by whom, how often? What do they use today? What went wrong last time?
*Rewrite:* "The operations director decides weekly staffing using a spreadsheet assembled manually over 6 hours from three systems; it's often a week out of date. Solved when the director gets an automatically refreshed staffing view every Monday by 9am, accurate to within 2% of source systems."

**5. "…99.9% accuracy by next month."**
*Wrong:* prescribes the technique (ML); the target and timeline are arbitrary and probably unrealistic; there's no baseline time or current error rate.
*Ask:* What's the current processing time and error rate? What does an error cost? Is human review acceptable for uncertain cases?
*Rewrite:* "Accounts-payable staff take a median of 12 minutes per invoice, with a 3% keying-error rate. Target: median under 3 minutes and errors ≤ 1%, using automated extraction plus human review of low-confidence fields, measured over a 4-week pilot."
