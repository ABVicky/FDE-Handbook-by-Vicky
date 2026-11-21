# Case 03 — Permissions first

🧪 **Illustrative composite.** Not about a real company.
**Industry:** Healthcare · **Lifecycle focus:** Design, Validate, Deploy

## Situation
A large hospital wants an AI assistant so staff can ask questions like "What's the protocol for a needle-stick injury?" instead of searching a shared drive of ~2,000 policy documents. A prototype built in two weeks impresses the innovation team.

*Stop here. What could go wrong in production?*

## What the FDE found during validation
- Some documents were **restricted** (HR investigations, executive pay policy, legal matters). The prototype indexed everything, so any user could retrieve them.
- About 15% of documents had **newer versions** elsewhere on the drive; the assistant sometimes quoted outdated clinical protocols.
- The hospital's information-governance team had not been consulted and had to approve any system touching staff data.

## What was built
1. Integration with the hospital's identity system (SSO), so the assistant knew who was asking.
2. **Document-level permissions** enforced at retrieval time, mirroring the shared drive's access rules.
3. Effective-date and "superseded" metadata; outdated documents excluded by default.
4. Answers always show **citations** to the source document and version; "I don't know" when the documents don't cover a question.
5. An evaluation set of real staff questions, reviewed by clinical leads, including adversarial questions designed to extract restricted content.

## What went wrong
- Launch slipped by six weeks to pass governance review. The FDE's early prototype had skipped the people who could block it.
- Mirroring permissions was harder than expected: the shared drive's permissions were themselves inconsistent and had to be cleaned up first.

## Outcome (illustrative)
The assistant launched to a pilot ward, then hospital-wide. Staff trust was high because every answer cited its source, and there were no permission incidents in the pilot.

## Lessons
- In regulated settings, **security and permissions are features**, not add-ons.
- Involve the people who can say "no" (security, governance, legal) in the Design stage.
- Citations and "I don't know" build more trust than fluent answers.

## Discussion questions
1. At which lifecycle stage should governance have been involved? What would you have asked them?
2. How would you test that permissions really work?
3. Who in the hospital should own the assistant after handover?
