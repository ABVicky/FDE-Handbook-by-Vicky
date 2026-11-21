# Exercise 04 — Review a pull request

A colleague opens this PR: **"Add CSV export endpoint for the director."** Review it as you would on GitHub: list each issue, why it matters, and a suggested fix. Order them by severity.

```python
@router.get("/export")
def export(repo: Repository = Depends(get_repo)):
    leads, _ = repo.list_leads(limit=100)
    rows = "lead_id,name,phone,email\n"
    for l in leads:
        rows += f"{l.lead_id},{l.name},{l.phone},{l.email}\n"
    print("exported", rows)
    return Response(rows, media_type="text/csv")
```

PR description: *"Works on my machine."*
