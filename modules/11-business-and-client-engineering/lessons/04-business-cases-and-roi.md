# Lesson 04 — Business cases and ROI

**Time:** ~4 hours · **Core**

## Why

Ms. Rao's board asked: *"What did we get for the money?"* A business case answers that **before** the work (should we do it?) and **after** (did it work?). FDEs who can build an honest one earn the trust to do the next project.

## The parts of a business case

1. **Problem and baseline:** what happens today, in numbers
2. **Proposed change** and how it's expected to move the numbers
3. **Benefits:** revenue, cost, risk, with the reasoning
4. **Costs:** one-off and running, **including the client's own people's time**
5. **Assumptions**, each labelled with who provided or agreed it
6. **Scenarios:** conservative / middle / optimistic
7. **How we'll measure it** after launch

## AdmitFlow's ROI model

[`exercises/solutions/roi_model.py`](../exercises/solutions/roi_model.py) separates **measured** numbers from **assumptions**:

```
Measured on 3000 past leads: enrolment 16.2% if contacted within 24h, 5.9% if later.
Assumed shift: 45% → 85% of 9,000 enquiries a year contacted within 24h.
Today's expected enrolments from these enquiries: about 949 a year.

scenario       extra enrol.  vs today    revenue  contribution  net year 1   payback
conservative           91.9       10%    399,763       139,917      96,597     2.8 mo
middle                183.8       19%    799,525       279,834     236,514     1.4 mo
optimistic            275.7       29%  1,199,288       419,751     376,431     0.9 mo
```

How it was made honest:
- **Correlation isn't causation.** Leads called quickly may differ in other ways (they enquired in office hours, they're keener). The model assumes only 25–75% of the observed gap is *caused* by speed (`causal_share`).
- **Contribution, not revenue.** An extra student brings fees but also costs to teach; the model counts 35% as contribution.
- **Hidden costs included.** Contacting 85% of leads within a day needs more counsellor time, so the model adds a part-time counsellor.
- **Sanity check.** The first version (revenue only, no extra counsellor) showed payback in under a month. When a business case looks that good, look for what's missing before presenting it.
- **Compared with today** (about 949 enrolments a year), so "+92" means "+10%", which people can judge.

## Presenting it

Lead with the **conservative** case. Clients forgive under-promising; they don't forget over-promising.

> *"Based on two years of your own data, getting 85% of enquiries contacted within a day is likely to add 90–280 enrolments a year (10–30%). Even in the cautious case, the project and an extra part-time counsellor pay for themselves within one intake. The pilot will tell us which end of the range is right."*

## Measuring after launch

Plan the measurement **before** launch:
- **Baseline** the metric for a period before (the pilot measured the real 24-hour rate)
- **Compare like with like:** same intake period year on year, or a staged rollout (some counsellors first) as a rough control group
- **Report regularly** in the client's own reports (Ms. Rao's board pack)
- **Separate effects:** if ad spend also changed, say so

## Time savings: count carefully

"15 hours a week saved" is only a *financial* saving if those hours are used for something valuable (more calls) or reduce a cost. Otherwise present it as capacity freed, not money saved.

## Check yourself

Do [Exercise 02](../exercises/02-roi.md): change three assumptions you think are too optimistic, re-run the model, and write the one-paragraph summary for the board. Then list what the pilot must measure to replace your two most uncertain assumptions with facts.

Next: [Lesson 05 — Communicating with stakeholders](05-communication.md)
