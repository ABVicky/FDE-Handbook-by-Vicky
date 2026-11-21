# Exercise 04 — Model answers (Ubuntu 24.04)

1. **Service user and directory**
   ```bash
   sudo useradd --system --create-home --shell /usr/sbin/nologin admitflow
   sudo mkdir -p /opt/admitflow && sudo chown admitflow:admitflow /opt/admitflow
   ```
2. **Secret file readable only by root and the group**
   ```bash
   sudo mkdir -p /etc/admitflow
   echo "ADMITFLOW_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')" | sudo tee /etc/admitflow/env >/dev/null
   sudo chown root:admitflow /etc/admitflow/env && sudo chmod 640 /etc/admitflow/env
   ls -l /etc/admitflow/env      # -rw-r----- 1 root admitflow …
   ```
3. **Who's on the port, then stop it:** `sudo ss -ltnp | grep :8000` shows the PID; `kill <PID>` (or `sudo systemctl stop <service>` if it's a service, otherwise it'll just restart).
4. **Recent logs:** `journalctl -u ssh -n 10 --no-pager` (in a container without systemd: `tail -n 10 /var/log/…`, or check the program's own output).
5. **Largest directories:** `sudo du -h --max-depth=1 /var 2>/dev/null | sort -h | tail -5`
6. **Backup before editing:** `sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak-$(date +%F)`
7. **Firewall:** `sudo ufw allow OpenSSH && sudo ufw allow 443/tcp && sudo ufw enable && sudo ufw status`. In a container, network exposure is controlled by the container runtime (`-p` / `ports:`), and containers usually lack the privileges to change host firewall rules.
8. **systemd unit** `/etc/systemd/system/demo-http.service`:
   ```ini
   [Unit]
   Description=Demo HTTP server
   After=network.target

   [Service]
   User=admitflow
   WorkingDirectory=/opt/admitflow
   ExecStart=/usr/bin/python3 -m http.server 8000
   Restart=on-failure
   RestartSec=2

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl daemon-reload && sudo systemctl enable --now demo-http
   sudo systemctl kill -s KILL demo-http; sleep 3; systemctl status demo-http   # active again: restarted
   ```
   (`Restart=on-failure` restarts after a crash or kill signal, but not after a clean `systemctl stop`.)
