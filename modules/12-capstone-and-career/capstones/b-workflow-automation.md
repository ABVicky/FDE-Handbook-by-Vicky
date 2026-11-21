# Capstone B — Intelligent workflow automation

## The client
**Meridian Supplies** (fictional), a wholesaler, receives ~1,200 supplier invoices a month by email (PDF, photos, some Excel). Two accounts-payable clerks type each into their ERP: supplier, invoice number, date, line items, tax, total, purchase-order number. Errors cause late-payment penalties and duplicate payments.

## What they say
- **Finance director:** "I want processing time halved, and duplicate payments to stop. I don't trust a robot to pay anyone."
- **AP clerk:** "The hard ones are the photos and the suppliers who put the PO number in a weird place."
- **IT:** "The ERP has a REST API for creating draft invoices. Nothing writes to it without approval."

## Your data
Create 100+ synthetic invoices from at least 15 fictional suppliers, in varied layouts (clean PDFs, rotated scans, phone photos, multi-page), with ground-truth fields. Include duplicates, wrong totals, missing PO numbers and one obvious fraud attempt (changed bank details).

## Hard requirements
- Extraction (OCR and/or a multimodal model) with **per-field confidence**
- Validation rules: totals add up, PO exists, supplier bank details unchanged, duplicate detection
- A **review queue** UI: clerks see the document next to extracted fields, correct and approve
- Approved invoices posted to a (mock) ERP API idempotently
- Evaluation: field-level accuracy against ground truth, share auto-approved vs reviewed, duplicate/fraud detection rate
- Audit log of every change and approval

## Questions to settle in discovery
What's the acceptable error rate per field? Which suppliers make up 80% of volume? What happens today when bank details change?
