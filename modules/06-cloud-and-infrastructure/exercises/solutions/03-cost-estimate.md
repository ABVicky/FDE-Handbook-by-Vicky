# Exercise 03 — Model answer: how to present a cost estimate

> This handbook deliberately doesn't quote prices: they change and vary by region. The *method* and the *presentation* are what's being assessed. Fill in the numbers from the calculator on the day, and date them.

## Resources and assumptions (Google Cloud example; equivalents in brackets)

| Resource | Sizing assumption | Cost driver | Monthly (from calculator, dated) |
| --- | --- | --- | --- |
| Cloud Run API (App Runner / Container Apps) | 6 users × ~300 requests/day; scale to zero; max 3 instances | vCPU-seconds, requests | low: free tier · high: _ |
| Cloud SQL PostgreSQL (RDS / Azure DB) | smallest shared-core tier, 10 GB SSD, automated backups, 7-day retention | **always-on instance hours**: usually the largest line | _ |
| Dashboard hosting (S3+CloudFront / Static Web Apps) | < 1 GB, < 5 GB transfer | storage + egress | ≈ negligible |
| Secret Manager (Secrets Manager / Key Vault) | 2 secrets, low access | per secret + access | small |
| Artifact Registry (ECR / ACR) | keep last 10 images (~2 GB) | storage | small |
| Logging (CloudWatch / Azure Monitor) | ~1 GB/month, 30-day retention | ingestion volume | often within free allowance |
| Scheduled ingest job | weekly, < 1 minute | job seconds | ≈ negligible |

**Range:** low / expected / high, with the dominant item called out ("~80% of the cost is the database instance").

## Biggest risks to the estimate

1. **Database tier too small** → slow under load → pressure to upgrade. *Control:* load-test with realistic volume (Module 05 break & fix data) before go-live; agree the upgrade path and its cost in advance.
2. **Forgotten resources** (test databases, old images, unused IPs). *Control:* labels on everything, monthly review, delete experiments the same day.
3. **Log volume explosion** (debug logging left on, a crash loop). *Control:* `INFO` level in production, retention limits, budget alert.

## Budget alerts

- 50% of monthly budget → FDE + Mr. Okafor (email)
- 90% → FDE + Mr. Okafor + Ms. Chen
- 100% → same, plus a same-day review
- Also a *forecast*-based alert if the provider supports it

## Summary for Ms. Chen (≈ 100 words)

> AdmitFlow's expected running cost is **[X–Y] per month**, based on the provider's pricing calculator on [date]. About four-fifths is the managed database, which includes daily backups. The rest (web hosting, storage, logs) is small and rises only slightly with use. Costs are fixed unless usage grows well beyond today's six counsellors. I've set alerts at 50%, 90% and 100% of [budget], going to you and Mr. Okafor, and I'll review the actual bill with you after the first month. The main risk is needing a larger database if usage grows; that would be agreed with you first.
