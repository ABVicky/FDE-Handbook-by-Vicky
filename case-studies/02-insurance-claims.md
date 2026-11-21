# Case 02 — The 98% demo

🧪 **Illustrative composite.** Not about a real company.
**Industry:** Insurance · **Lifecycle focus:** Prototype, Validate

## Situation
An insurer wants to automate reading incoming claim documents. During the sales process, the vendor showed a demo extracting claim fields with "98% accuracy." After the contract was signed, an FDE was assigned to put it into production.

*Stop here. What would you check first?*

## What the FDE found
- The demo's 98% was measured on **40 clean, typed PDFs** the vendor had prepared.
- Real incoming claims included phone photos of forms, handwritten notes, multi-claim bundles and documents in two languages.
- On a sample of 200 real (anonymized) claims, accuracy was **~70%**.
- Claims handlers didn't need every field. They needed six fields reliably, plus a flag for anything suspicious.

## What was built
1. A **test set** of 200 real claims with hand-checked answers, agreed with the claims team as the acceptance benchmark.
2. Extraction focused on the six fields that mattered, with a confidence score per field.
3. Pre-processing for photos (deskewing, orientation detection) and routing for handwritten forms.
4. A **human review queue** for low-confidence fields, so the system never silently guessed.
5. Automated evaluation runs on every change, so improvements could be proven, and regressions caught.

## What went wrong
- Expectations set by the sales demo created early tension. The FDE had to reset them openly.
- Building the labelled test set took longer than any model work, because claims experts had limited time.

## Outcome (illustrative)
Over several iterations, accuracy on the six key fields reached the agreed target, with roughly a fifth of claims routed to human review. Handlers' review time per claim fell significantly.

## Lessons
- A demo on clean data proves almost nothing about production.
- The test set *is* the contract. Agree on it with the client.
- "Confidence + human review" often beats chasing the last few percent of accuracy.

## Discussion questions
1. How would you tell the client that real accuracy is ~70% after they were shown 98%?
2. Who should decide the acceptable share of claims sent to human review, and how?
3. How would you prevent this gap in the next sale? (Hint: FDEs feed back to the company.)
