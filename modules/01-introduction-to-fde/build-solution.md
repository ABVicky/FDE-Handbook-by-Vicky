# Module 01 Build — Reference Solution

> ⚠️ Finish your own discovery pack first. This is *one* good answer, not the only one.

## 1. Stakeholder map

| Stakeholder | Role | Cares about | Influence | Affected | Possible resistance |
| --- | --- | --- | --- | --- | --- |
| Ms. Rao | Director, sponsor | Admissions growth, ad ROI, keeping up with competitors | H | M | Attached to the "chatbot" idea; may feel overruled |
| Mr. Fernandes | Head of Admissions | Counsellor workload, no missed leads | H | H | Fear of being measured; previous tools that failed |
| Counsellors (6), e.g. Priya | Daily users | Less copying, fewer duplicate calls, hitting targets | M | **H** | New tool = extra work; worry about activity tracking |
| Mr. Okafor | Part-time IT | Nothing hard to maintain; security | M | M | Will block anything he can't support |
| Ms. Chen | Finance | Predictable cost, data protection | M | L | Cost overruns; compliance risk |
| **Reception staff** *(missing)* | Take phone and walk-in enquiries | Quick capture, fewer interruptions | L | H | Extra data entry |
| **Marketing / ad agency** *(missing)* | Runs ads, owns lead-form exports | Proving their ads work | M | M | Attribution may make them look bad |
| **Prospective students** *(missing)* | End customers | Fast, accurate answers | — | H | Spammy follow-ups; privacy |

## 2. Discovery questions (excerpt: 15 total)

**Head of Admissions**
1. In the last intake, roughly how many enquiries were there, and how many became admissions? *(baseline)*
2. How do you decide which counsellor handles which enquiry?
3. When a student enrols elsewhere, how do you find out, and what reasons do they give?

**Counsellors**
4. Walk me through your last ten enquiries: where did each come from and what did you do? *(observe)*
5. How long does it take from an enquiry arriving to your first call? *(baseline)*
6. Which questions do students ask most? Could you list the top 20?
7. What would make you stop using a new tool after a week?

**Director**
8. If this works, what would be different in six months? What number would you show the board?
9. When you picture the chatbot, what problem is it solving for you? *(tests the chatbot assumption)*

**IT**
10. Where does each type of enquiry data live today, and who can access it? *(data)*
11. Does the student information system have any export or API? *(data)*
12. What can you realistically maintain each month? *(constraint)*

**Finance**
13. What's the monthly ad spend by channel, and the average fee per admission? *(baseline)*
14. What monthly running cost would be acceptable? *(constraint)*
15. What happened in the previous data-protection complaint? *(constraint)*

**Observation:** sit with reception for a morning peak and with one counsellor for half a day.

## 3. Problem statement

> Prospective students who enquire at Northbridge Institute through any of five channels often wait more than a day for a response or are never contacted. Only about **45%** of enquiries are contacted within 24 hours *(estimate from Head of Admissions; to be measured)*. Enquiries are scattered across an inbox, ad exports, paper forms, spreadsheets and counsellors' phones, so duplicates are common, missed leads go unnoticed, and leadership cannot tell which channels or ads produce admissions.
>
> With 600–900 enquiries a month and a ~9% conversion rate, even a small improvement in response speed is likely to mean significant additional admissions per intake *(to be quantified with finance data)*.
>
> **We'll consider this solved when**, for the next intake, at least 90% of enquiries receive a first response within 24 hours, duplicate counsellor contacts are near zero, and leadership can see enquiry-to-admission conversion by channel. **Constraints:** operable by one part-time IT administrator, predictable monthly cost agreed with finance, compliant with data-protection rules, and the first improvements in place within 10 weeks.

## 4. Success metrics

| Metric | Definition | Measured by | Baseline | Target | Time frame |
| --- | --- | --- | --- | --- | --- |
| Speed to first contact | % of unique enquiries with a logged first contact within 24 h | Timestamps in the central lead record | ~45% (estimate) | ≥ 90% | Next intake |
| Duplicate contacts | % of students contacted by more than one counsellor for the same enquiry | Dedup report | Unknown, measure in week 1 | < 2% | 6 weeks after launch |
| Conversion visibility | Leadership report showing enquiries → admissions by channel | Weekly report exists and matches finance's admissions count | None | Weekly, ±2% of finance figures | 8 weeks |

**Top unknowns**
1. Actual baseline response time and conversion by channel
2. Whether the student information system can export admissions data
3. How counsellors are currently assigned and measured
4. What students ask most, and whether answers are documented anywhere
5. Data-protection requirements for storing and messaging students

**Reply to the director**

> Thank you, Ms. Rao. An assistant that answers students' questions may well be part of the solution, and we'll keep it on the table. What we heard, though, is that many students aren't getting a reply at all, because enquiries are spread across five channels and duplicated. A chatbot on the website alone would reach only about a third of enquiries. I'd suggest we first bring all enquiries into one place so every student gets a fast response and you can finally see which ads work. Can we spend two days next week with your counsellors and reception to confirm this?
