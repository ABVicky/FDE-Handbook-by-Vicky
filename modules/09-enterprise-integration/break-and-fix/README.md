# Module 09 — Break & Fix: 240 contacts for 99 students

**Time:** 1–2 hours · Do this after [Lesson 04](../lessons/04-calling-third-party-apis.md).

## The situation

The marketing team syncs AdmitFlow leads into their CRM every night, using a script a contractor wrote: [`naive_crm_sync.py`](naive_crm_sync.py). Its selling point: *"Robust: retries on any network error!"*

After a week, marketing complains: students are receiving the same newsletter three or four times, and the CRM's contact count is far higher than the number of enquiries.

The CRM is simulated by [`flaky_crm.py`](flaky_crm.py): it behaves like a real API on a real network, where occasionally a request **succeeds on the server but the response is lost**.

```bash
cd modules/09-enterprise-integration/break-and-fix
```

```bash
python naive_crm_sync.py
```

```
leads with email: 99
contacts in CRM:  240
duplicates:       141
```

## Your job

1. Explain **both** ways this script creates duplicates. (There are two separate mechanisms.)
2. Fix it so that any number of runs, with any number of lost responses, ends with **exactly one contact per student**.
3. Prove it with a test against `FlakyCrm`.
4. Write a short plan for cleaning up the existing duplicates in marketing's CRM, safely.

## Hints

<details><summary>Hint 1</summary>What happens on the CRM side when <code>create_contact</code> retries after a <code>ReadTimeout</code>?</details>

<details><summary>Hint 2</summary>What does the script remember between nightly runs? How does run 2 know a student was already synced?</details>

<details><summary>Hint 3</summary>Before creating, what could you ask the CRM? After creating, what must you save, and where?</details>

When you're done: [SOLUTION.md](SOLUTION.md)
