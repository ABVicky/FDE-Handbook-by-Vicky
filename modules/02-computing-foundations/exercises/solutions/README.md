# Module 02 — Solutions

There's usually more than one correct command. If yours gives the same answer for the right reason, it's correct.

---

## Lesson 03 check yourself

```bash
tail -n +2 leads_sample.csv | grep -v '^$' | cut -d, -f2 | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -5
```

```
  10 2026-09-12
   9 2026-09-23
   6 2026-09-26
   6 2026-09-21
   6 2026-09-20
```

(Ties may print in a different order on your machine.) Field 2 comes *before* the name, so quoted commas in names don't affect it.

---

## Exercise 01 — Terminal scavenger hunt

1. `echo ~` or `echo $HOME`
2. `cd ~/projects/fde-handbook && pwd`
3. `ls -la`: the `.git` folder holds Git's history and settings for the repository.
4. `find modules -name "*field-track*.md"`, then add `| wc -l` to count. (Number depends on how many modules are written.)
5. `grep -rn "APP_PORT" .`
6. `mkdir -p ~/fde-practice/m02/notes`
7. `cp projects/admitflow/data/leads_sample.csv ~/fde-practice/m02/leads.csv`
8. `ls -l ~/fde-practice/m02/leads.csv`, then `chmod o-r ~/fde-practice/m02/leads.csv`, then `ls -l` again
9. `echo "Module 02 started" > ~/fde-practice/m02/notes/log.txt`, then `date >> ~/fde-practice/m02/notes/log.txt`
10. `python3 -m http.server 8123 &`, then `ps aux | grep "http.server 8123"`, then `kill <PID>`, then run `ps` again
11. `ls ~/fde-practice/m02/leads.csv`, then `rm ~/fde-practice/m02/leads.csv`

---

## Exercise 02 — Pipelines on leads

**1.** `wc -l leads_sample.csv` → **123** lines. One is the header and **two are blank**:

```bash
grep -c '^$' leads_sample.csv
```

So 123 − 1 − 2 = **120 leads**. (Blank lines in exported data are common and break naive counts.)

**2.** **20**

```bash
grep -c '^ENQ-[0-9]*,2026-09-0[1-7]' leads_sample.csv
```

**3.** **8** names in quotes:

```bash
grep '"' leads_sample.csv | cut -d'"' -f2
```

**4.** **15**. Counting fields from the *end* avoids the quoted-comma problem:

```bash
tail -n +2 leads_sample.csv | awk -F, 'NF && $(NF-3)==""' | wc -l
```

**5.** The naive `cut -d, -f6` is **wrong**: on the 8 rows with `"Last, First"` names, the extra comma shifts every column, so field 6 is an email address instead of a course. You'll also see 2 empty values from the blank lines (plus 2 from quoted rows with no email). Counting from the end fixes it, because the course is always second-to-last:

```bash
tail -n +2 leads_sample.csv | awk -F, 'NF {print $(NF-1)}' | sort | uniq -c | sort -rn
```

```
  25 Nursing Assistance
  23 Digital Marketing
  22 Business Administration
  17 Web Development
  17 Accounting
  16 Data Analytics
```

**6.** **Nursing Assistance** (4 of 11). Note the `tolower`, because source values have inconsistent capitalization:

```bash
tail -n +2 leads_sample.csv | awk -F, 'NF && tolower($NF) ~ /whatsapp/ {print $(NF-1)}' | sort | uniq -c | sort -rn
```

**Reflection (sample):** text tools are fast for exploring, but CSV isn't just "split on commas." Quoted fields, blank lines and inconsistent values silently produce wrong numbers. For anything a client will rely on, use a real CSV parser and check your totals add up.

---

## Exercise 03 — HTTP with curl

1. `curl -s -o /dev/null -w "%{http_code}\n" https://example.com` → `200`
2. Look for `Connected to example.com (<IP>) port 443`, `SSL connection using TLSv1.3` (or 1.2), and `< content-type: text/html`.
3. `404`
4. `301` (or another 3xx). `Location: https://github.com/`. The site redirects all plain HTTP to HTTPS so traffic is encrypted.
5. An HTML page listing the files in the folder.
6. `curl -o /tmp/downloaded.csv http://localhost:8000/leads_sample.csv && diff /tmp/downloaded.csv leads_sample.csv`: no output from `diff` means identical.
7. `501 Unsupported method ('POST')`. Python's simple server only implements GET and HEAD. Terminal 1 logs the request with code 501.
8. `curl: (7) Failed to connect to localhost port 8000 … Connection refused`. Nothing is listening on the port: "connection refused," not a timeout.
9. Should mention: `localhost` resolves to `127.0.0.1`, curl opens a TCP connection to port 8000, sends `GET /`, the Python process receives it, responds `200` with HTML, and curl prints the body.

---

## Exercise 04 — Map the network

1. Usually `192.168.x.x` or `10.x.x.x`: a private range.
2. Large sites often return several addresses (or different ones over time) to spread load and provide redundancy.
3. `NXDOMAIN` (dig) or `can't find … Non-existent domain` (nslookup).
4. `lsof -nP -iTCP -sTCP:LISTEN`: typical entries include system services, sync tools, or development servers.
5. `OSError: [Errno 48] Address already in use` (macOS) or `[Errno 98]` (Linux). Find the owner with `lsof -i :8000`.
6. Port 443: `succeeded` / `open`: something is listening. Port 81: times out: a firewall drops it, so there's no "refused" reply. That's the timeout-vs-refused distinction from Lesson 05.
7. Laptop (private IP, random high port) → router → internet → example.com (public IP, port 443), with a DNS lookup beforehand.
