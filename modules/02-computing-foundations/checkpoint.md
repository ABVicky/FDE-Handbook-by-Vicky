# Module 02 — Checkpoint

Pass mark: **8 / 10**, plus the [build task](build.md) and [break & fix](break-and-fix/README.md), to skip this module.

---

**1.** A program is running slowly and your laptop's memory is almost full. What is most likely happening?
- a) The CPU is overheating
- b) The operating system is moving data between RAM and disk (swapping)
- c) The hard drive is full
- d) The internet connection is slow

**2.** What does `ls -l` showing `-rw-r--r--` for `deploy.sh` tell you, and what command lets you run it as `./deploy.sh`? *(Short answer)*

**3.** What does this command print?
```bash
cat leads.csv | grep -i website | wc -l
```
- a) The first line of every website lead
- b) The number of lines containing "website" in any capitalization
- c) All lines that don't contain "website"
- d) The file size of leads.csv

**4.** You run `python3 app.py` and get `command not found: python3`, but Python is installed. What's the most likely cause?
- a) The file `app.py` is missing
- b) The directory containing `python3` isn't in your `PATH`
- c) Python 3 can't run scripts
- d) You need to restart the internet

**5.** What's the difference between `export API_KEY=abc` and `API_KEY=abc` in a shell? *(Short answer)*

**6.** Match each item to what it does: **DNS · IP address · port · TLS**
- i) Identifies a specific machine on a network
- ii) Translates `example.com` into a machine's address
- iii) Encrypts traffic between client and server
- iv) Identifies which program on a machine should receive traffic

**7.** What does `127.0.0.1` (or `localhost`) refer to?

**8.** A web request returns status **401**. Then, after logging in, a different page returns **403**. What's the difference?

**9.** `curl https://api.client.com` fails with `Could not resolve host`. The client's IT team tells you the server's IP is `10.20.0.15`, and `ping 10.20.0.15` gets replies. Where's the problem?
- a) The server is down
- b) DNS
- c) The firewall blocks port 443
- d) The TLS certificate expired

**10.** A server says `listening on 0.0.0.0:8000` but `curl localhost:9000` gives `Connection refused`. What's wrong?

---

<details>
<summary><strong>Answers</strong></summary>

1. **b**: when RAM is full, the OS swaps to disk, which is much slower.
2. The file is readable and writable by the owner and readable by others, but **not executable**. Fix with `chmod +x deploy.sh`.
3. **b**: `grep -i` matches case-insensitively; `wc -l` counts lines.
4. **b**: the shell searches only the directories listed in `PATH`.
5. `export` makes the variable available to **child processes** (programs you start). Without it, only the current shell sees it.
6. DNS → ii · IP address → i · port → iv · TLS → iii.
7. The current machine itself (the loopback address). Traffic never leaves the computer.
8. **401 Unauthorized:** the server doesn't know who you are (not logged in / bad credentials). **403 Forbidden:** it knows who you are, but you're not allowed.
9. **b**: the machine is reachable by IP, so the network path is fine; the *name* can't be turned into an address.
10. Wrong port: the server is on 8000, the request went to 9000.

</details>
