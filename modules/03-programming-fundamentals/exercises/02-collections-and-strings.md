# Exercise set 02 — Collections and strings

Use this data (copy it into your file):

```python
LEADS = [
    {"name": "  GRACE PATEL ", "email": "Grace.Patel91@Example.com", "source": "Website ", "course": "Accounting"},
    {"name": "Lee, Chloe", "email": "chloe.lee95@example.com", "source": "website", "course": "DA"},
    {"name": "grace patel", "email": "grace.patel91@example.com", "source": "ad", "course": "Accounting"},
    {"name": "Nguyễn Thu", "email": "thu@example.org", "source": "ad", "course": "web_dev"},
    {"name": "प्रिया शर्मा", "email": "", "source": "WhatsApp", "course": "Nursing"},
    {"name": "José Chen", "email": "jose@example.org", "source": "ad", "course": "DA"},
]
```

1. **`clean_name(raw)`**: collapse whitespace, turn `"Last, First"` into `"First Last"`, title-case only if the input is all upper or all lower case, and NFC-normalize. Check: `clean_name("José Chen") == "José Chen"` (one code point for é).
2. **`unique_emails_per_source(leads)`**: return a dict `{source: number of unique emails}`, with sources normalized (`strip().lower()`), emails lower-cased, and empty emails ignored. Expected: `{"website": 2, "ad": 3, "whatsapp": 0}`.
3. **`courses(leads)`**: map course codes to full names with a lookup dict (`DA` → `Data Analytics`, `web_dev` → `Web Development`, `Nursing` → `Nursing Assistance`), and return a `Counter` of full names.
4. **`group_names_by_source(leads)`**: return `{source: sorted list of cleaned names}` using `defaultdict(list)`.
5. **`find_duplicates(leads)`**: return the list of emails (lower-cased) that appear more than once. Use a set, in one pass.
6. In a comment: why is `find_duplicates` with a set much faster than checking `email in list_of_seen_emails` for 1 million leads?
