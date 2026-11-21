# Module 07 — Checkpoint

Pass mark: **8 / 10**, plus the [build](build.md) and [break & fix](break-and-fix/README.md).

---

**1.** Give one AdmitFlow example each where the right tool is (a) a rule, (b) a report, (c) a classic ML model, (d) an LLM.

**2.** What is target leakage? Name two leaky columns in `historical_leads.csv`.

**3.** Why train on 2024 and test on 2025 instead of a random split?

**4.** 11% of leads enrol. A model is "89% accurate." Is that good?

**5.** Define precision and recall in terms of calling leads.

**6.** What does ROC AUC 0.5 mean? 0.6? 1.0?

**7.** Model AUC 0.605, baseline 0.609, on ~160 positives. What do you tell the client?

**8.** Why does AdmitFlow show "high / medium / low" and reasons instead of the probability?

**9.** What should happen to AdmitFlow if the model file is missing?

**10.** What is an embedding, and why does it beat TF-IDF for matching "will I get a job afterwards?" to "Is there a placement guarantee?"

---

<details>
<summary><strong>Answers</strong></summary>

1. (a) Flag leads waiting > 24h; (b) conversion by channel; (c) lead scoring from past outcomes; (d) answering students' questions from course documents.
2. Using information not available at prediction time, usually caused by or caused by the outcome. `fee_paid`, `days_to_final_status` (also `hours_to_first_contact`, `contacts_first_week`, which are actions taken after arrival).
3. It mirrors real use (predict future leads from past ones) and exposes changes over time (2025's base rate is lower). Random splits overstate performance.
4. No. "Always say no" gets ~89%. Accuracy alone is meaningless on imbalanced data.
5. Precision: of the leads we called first, the share who enrolled. Recall: of everyone who enrolled, the share we called first.
6. 0.5 = random ranking; 0.6 = weak but better than random; 1.0 = perfect ranking.
7. They're effectively tied: the model adds little beyond ordering by channel. Recommend focusing on response time, and use the model, if at all, as a tie-breaker.
8. Probabilities with three decimals imply false precision; bands are honest about uncertainty, and reasons let counsellors sanity-check (and helped find a bug).
9. Scoring endpoints return 503; everything else works normally. Optional ML must not break the core system.
10. A vector representing meaning, where similar meanings are close. TF-IDF needs shared words; those questions share none, but an embedding model places them close because they mean similar things.

</details>
