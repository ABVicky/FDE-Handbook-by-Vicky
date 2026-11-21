# Lesson 02 — Linux servers and SSH

**Time:** ~4 hours · **Core**

## Why this matters

Even in a world of managed services, you'll SSH into servers: the office VM, a client's jump host, a container to inspect logs. Being calm and careful on a server someone else owns is a core FDE trait.

## Connecting with SSH

SSH gives you an encrypted terminal on a remote machine.

```bash
ssh priya@10.20.0.15
```

### Use keys, not passwords

Create a key pair once (the private key stays on your laptop; you give out only the public key):

```bash
ssh-keygen -t ed25519 -C "your-name-laptop"
```

```bash
ssh-copy-id priya@10.20.0.15
```

A `~/.ssh/config` entry saves typing:

```
Host northbridge-vm
    HostName 10.20.0.15
    User priya
    IdentityFile ~/.ssh/id_ed25519
```

Then `ssh northbridge-vm`. Many organizations require going through a **bastion/jump host**: add `ProxyJump bastion.northbridge.example`.

**Never share private keys**, never paste them into chat, and use a passphrase.

### Copying files

```bash
scp data/admissions_export.csv northbridge-vm:/tmp/
```

## Finding your way around a server

| Question | Command |
| --- | --- |
| What OS and version? | `cat /etc/os-release` |
| How much disk is free? | `df -h` |
| What's using the disk? | `du -sh /var/* \| sort -h` |
| Memory? | `free -h` |
| What's running? | `ps aux --sort=-%mem \| head`, `top` |
| What's listening? | `ss -ltnp` |
| Who am I, what can I do? | `whoami`, `id`, `sudo -l` |
| Recent logins / reboots | `last`, `uptime` |

## Services with systemd

On most Linux servers, long-running programs are **services** managed by systemd:

```bash
systemctl status docker
```

```bash
sudo systemctl restart docker
```

```bash
journalctl -u docker --since "1 hour ago"
```

A service unit for AdmitFlow without Docker would look like:

```ini
# /etc/systemd/system/admitflow.service
[Unit]
Description=AdmitFlow API
After=network.target

[Service]
User=admitflow
WorkingDirectory=/opt/admitflow
EnvironmentFile=/etc/admitflow/env      # secrets here, readable only by root and admitflow (chmod 600)
ExecStart=/opt/admitflow/.venv/bin/admitflow serve --host 127.0.0.1 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then `sudo systemctl enable --now admitflow`. (Here `127.0.0.1` is right: a reverse proxy such as nginx on the same machine forwards public HTTPS traffic to it.)

## Firewalls

Expose as little as possible. On Ubuntu:

```bash
sudo ufw allow OpenSSH
```

```bash
sudo ufw allow 443/tcp
```

```bash
sudo ufw enable
```

The database port (5432) should **never** be open to the internet.

## Etiquette on someone else's server

- **Ask before installing anything**, and record what you install.
- Prefer read-only commands while investigating.
- Before changing a config file: `sudo cp file file.bak-$(date +%F)`.
- Don't restart shared services during working hours without warning.
- Keep a log of what you did (it becomes the runbook, Module 10).
- Leave nothing behind: temporary files, test users, open ports.

## Check yourself

On any Linux machine you can use (a cloud free-tier VM, WSL, or a container), find: OS version, free disk, the five processes using the most memory, and every listening port with the program behind it. Write down the commands. Then do [Exercise 04](../exercises/04-linux-drills.md).

Next: [Lesson 03 — Docker](03-docker.md)
