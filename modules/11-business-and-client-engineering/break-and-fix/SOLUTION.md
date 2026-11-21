# Break & Fix — Solution

> ⚠️ Try it properly first.

## Usage

```bash
python solution/adoption_report.py
```

```
counsellor w1   w2   w3   w4   w5   w6   w7   w8   trend      group
priya      42   45   44   47   46   48   45   47   →          adopted
omar       38   35   30   24   18   12   9    7    ↓          drifting away
lucia      20   14   8    3    1    0    0    0    ↓          drifting away
kofi       25   22   19   15   10   6    4    2    ↓          drifting away
mei        0    0    0    0    0    0    0    0    —          never started
arjun      30   28   27   26   27   25   26   24   →          adopted

2 of 6 counsellors use AdmitFlow fully; 3 are drifting back to spreadsheets; 1 never started.
```

If only a third of the team uses the system, the 24-hour metric can't move much. The software works; the **change** didn't happen.

## Root causes

| # | Cause | Type | Evidence |
| --- | --- | --- | --- |
| 1 | **The old process was never switched off:** the Friday spreadsheet is still required, so AdmitFlow is extra work | Process | Omar, Mr. Fernandes |
| 2 | **The manager's need wasn't met:** Mr. Fernandes manages through that spreadsheet; AdmitFlow has no team view he trusts | Product / requirements | Mr. Fernandes |
| 3 | **One rushed training session**, in English, with interruptions; no follow-up; no material to look back at | Training | Lucía, Mei |
| 4 | **People missed entirely:** Mei (on leave), reception (phone enquiries still in a notebook) | Training / scoping | Mei, Ana |
| 5 | **Mobile layout unusable** for counsellors who work at fairs and the other campus | Product | Kofi |
| 6 | **No "today's new leads" view**: the daily workflow wasn't designed around how counsellors work | Product | Arjun |
| 7 | **Support channel failed:** Google sign-in request unanswered; password resets go to IT | Ownership / communication | Mr. Okafor's email |
| 8 | **"Done" defined as "requirements delivered"**, declared on go-live day, with no adoption or outcome measure | Engagement design | Go-live email |

## Recovery plan (4 weeks)

| Week | Action | Owner | Measure |
| --- | --- | --- | --- |
| 1 | Agree with Mr. Fernandes to **retire the Friday spreadsheet**, replaced by a team view in AdmitFlow (built this week: per-counsellor open leads, contacted within 24 h, overdue follow-ups) | FDE + Mr. Fernandes | Spreadsheet no longer requested from week 2 |
| 1 | Turn on **Google sign-in** (Module 09); reply to Mr. Okafor | FDE | Password-reset requests → 0 |
| 1–2 | **Short training, per person**: 30 minutes each, at their desk or by video, in their preferred language; a one-page quick guide; Priya as the go-to champion | FDE + Priya | All 6 counsellors + reception trained |
| 1 | Show reception how to **add phone and walk-in enquiries** | FDE | Phone leads appearing in AdmitFlow daily |
| 2 | Fix the **mobile layout** of the lead list and detail panel; add **"New today"** and **"Due today"** filters | FDE | Kofi and Arjun confirm |
| 2–4 | **Weekly 15-minute check-in** with Mr. Fernandes: adoption per counsellor and the 24-hour metric | FDE + Mr. Fernandes | 6 of 6 active weekly; ≥ 85% contacted within 24 h by week 4 |
| 4 | Agree the **handover**: who owns training new staff, who answers questions, how issues reach the FDE | FDE + Mr. Fernandes + Mr. Okafor | Signed-off handover document |

## Reply to Ms. Rao

> Thank you for raising this, and I'm sorry I declared the project finished too early. AdmitFlow works, but only two of six counsellors use it fully, mainly because the old weekly spreadsheet is still required, training was one rushed session, and the mobile view doesn't suit counsellors working at fairs. None of that is the counsellors' fault. Over the next four weeks I'll work with Mr. Fernandes to replace the spreadsheet with a team view in AdmitFlow, train everyone individually, fix the mobile view, and switch on Google sign-in. We'll review the 24-hour contact rate together every week. I expect it above 85% by the end of next month, and I'll send you the numbers each Friday.

## What to do differently next time

- Define success as an **outcome** (24-hour contact rate) and **adoption**, not "requirements delivered"; measure both for weeks after go-live.
- Identify **every** user and stakeholder, including reception and the manager's own reporting needs (Module 01's stakeholder map listed reception as "missing").
- Plan **change management**: switch off the old process, train per person, appoint a champion.
- Design around a **day in the life** of each user (fairs, other campus, phone), not around features.
- Agree **support and ownership** before go-live.
