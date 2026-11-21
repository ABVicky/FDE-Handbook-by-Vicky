# AdmitFlow — Client Brief

> A fictional but realistic client. Every module adds to the system you build for them.
> Names, numbers and people are invented for learning purposes.

## The client

**Northbridge Institute of Professional Studies** (fictional) is a private institute offering 14 diploma and certificate courses: data analytics, digital marketing, accounting, nursing assistance, and others. It has two campuses and about 1,800 enrolled students.

## The situation

The institute receives **600–900 enquiries a month**, peaking before each intake. Enquiries arrive through:

| Channel | Approx. share | How it arrives today |
| --- | --- | --- |
| Website enquiry form | 35% | Email to a shared inbox |
| Social media ads (lead forms) | 30% | CSV export, downloaded "when someone remembers" |
| Phone calls | 15% | Written in a notebook at reception, later typed into a spreadsheet |
| Walk-ins and education fairs | 12% | Paper forms, typed in weekly |
| Messaging apps (e.g. WhatsApp) | 8% | Counsellors' personal phones |

Six **admission counsellors** follow up with leads. Each keeps a personal spreadsheet. Leadership sees a monthly admissions number but can't connect it back to channels or counsellor activity.

## What people say (from the first meeting)

> **Director (Ms. Rao):** "We spend a lot on ads and I have no idea which ones work. And I keep hearing that students enrolled elsewhere because nobody called them back. I want an AI chatbot like other institutes have."

> **Head of Admissions (Mr. Fernandes):** "My counsellors are drowning. The same student enquires three times through three channels and two counsellors call them. Others get missed completely."

> **Counsellor (Priya):** "Half my day is copying details between spreadsheets. Students ask the same twenty questions about fees, timings and placements."

> **IT Administrator (Mr. Okafor, part-time):** "We have a website on a hosting provider, Google Workspace for email, and an old student information system that runs on a server in the office. Please don't make me maintain anything complicated."

> **Finance Manager (Ms. Chen):** "Whatever you build, I need to know what it costs per month. And we've had a data-protection complaint before; student data must be handled properly."

## Known facts

- Estimated share of enquiries contacted within 24 hours: **~45%** (Head of Admissions' guess; not measured)
- Enquiry-to-admission conversion: **unknown** by channel; overall roughly 9% (approximate)
- Average course fee: varies; median about one month of a typical graduate salary (finance has exact figures)
- Monthly ad spend: significant; finance has exact figures
- Duplicate enquiries: "lots" (unmeasured)

## Constraints

- Small IT capacity: one part-time administrator
- Budget-conscious: monthly running costs must be predictable
- Student personal data is involved; local data-protection rules apply
- Counsellors use laptops at work and phones on the move
- The next intake opens in **10 weeks**

## What you, the FDE, have been asked to do

Ms. Rao has asked for "an AI chatbot." Your engagement lead has asked you to **run discovery first** and come back with a clear problem statement and success metrics before anyone commits to building anything.

That is your Module 01 build task: [modules/01-introduction-to-fde/build.md](../../modules/01-introduction-to-fde/build.md).

## Datasets (added in later modules)

| File | Added in | Description |
| --- | --- | --- |
| [`data/leads_sample.csv`](data/leads_sample.csv) | Module 02 | 120 synthetic enquiries from all channels, deliberately messy (blank lines, inconsistent channel names, quoted names with commas) |
| `data/ad_leads.csv` | Module 03 | Synthetic ad lead-form exports, different column names |
| `data/walkins.csv` | Module 03 | Typed-up paper forms, messy |
| `data/course_docs/` | Module 08 | Course brochures, fee schedules, FAQs |
