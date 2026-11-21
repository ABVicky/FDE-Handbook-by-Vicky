# Exercise 04 — Linux server drills

On a Linux machine (a free-tier cloud VM, WSL, or `docker run -it --rm ubuntu:24.04 bash`):

1. Create a user `admitflow` with no password login, and a directory `/opt/admitflow` it owns.
2. Create `/etc/admitflow/env` containing `ADMITFLOW_SECRET_KEY=…`, readable **only** by root and the `admitflow` group.
3. Find which process is listening on a port of your choice, and stop it.
4. Show the 10 most recent lines of a service's log with `journalctl` (or `/var/log/syslog` in a container).
5. Find the five largest directories under `/var`.
6. Make a dated backup copy of a config file before editing it.
7. Allow only SSH and HTTPS through the firewall (`ufw`) on a VM. Why not on a container?
8. Write a systemd unit that runs `python3 -m http.server 8000` as the `admitflow` user and restarts on failure. Enable it and prove it survives `kill`.
