# Lesson 04 — Environment variables, PATH and installing software

**Time:** ~2 hours · **Core**

## Why this matters

"It works on my machine" is very often an environment problem: a different Python, a missing variable, or a tool that isn't on the `PATH`. Configuration through environment variables is also how almost every production system (Docker, cloud, CI) passes settings and secrets to applications.

## Environment variables

An **environment variable** is a named value that a process can read. Every process has its own set, inherited from whoever started it.

```bash
echo $HOME          # read one
env                 # list all
export APP_PORT=8800      # set one, for this shell and programs it starts
echo $APP_PORT
unset APP_PORT            # remove it
```

**With and without `export`:**

```bash
GREETING=hello          # shell variable: only this shell sees it
export GREETING=hello   # environment variable: programs you start see it too
```

**For one command only:**

```bash
APP_PORT=9000 python3 server.py
```

### Why applications use them

Code stays the same everywhere; configuration changes per environment:

| Setting | On your laptop | In production |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://localhost/admitflow_dev` | the client's managed database |
| `LOG_LEVEL` | `debug` | `info` |
| `LLM_API_KEY` | your test key | the client's key, from a secrets manager |

In Python, reading one looks like this (you'll see it in the break & fix app):

```python
import os
port = int(os.environ.get("APP_PORT", "8000"))  # optional, with a default
data_dir = os.environ["ADMITFLOW_DATA_DIR"]      # required: crashes if missing
```

### `.env` files

Projects often keep local settings in a `.env` file:

```
APP_PORT=8800
ADMITFLOW_DATA_DIR=/home/priya/projects/admitflow/data
```

Load it into your shell with:

```bash
set -a; source .env; set +a
```

**Never commit `.env` files with secrets to Git.** Commit a `.env.example` with placeholder values instead, and add `.env` to `.gitignore`. Leaked API keys in public repositories are found and abused by automated scanners within minutes.

## PATH: how the shell finds programs

When you type `python3`, the shell searches each folder listed in the `PATH` variable, in order, and runs the first match.

```bash
echo $PATH
```
```
/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
```

```bash
which python3       # which file actually runs?
type -a python3     # all matches, in order
```

Common problems:

| Symptom | Likely cause |
| --- | --- |
| `command not found` right after installing something | Its folder isn't on `PATH`, or your shell hasn't reloaded. Open a new terminal |
| The "wrong version" runs | Another copy appears earlier in `PATH` |
| Works in your terminal but not in a script, cron job or service | That environment has a different, shorter `PATH` |

Adding a folder to `PATH` permanently: add a line to your shell's startup file (`~/.zshrc` for zsh, `~/.bashrc` for bash):

```bash
export PATH="$HOME/bin:$PATH"
```

## Installing software

| Platform | Package manager | Example |
| --- | --- | --- |
| macOS | Homebrew | `brew install jq` |
| Ubuntu/Debian/WSL | apt | `sudo apt install jq` |
| Windows (native) | winget | `winget install jqlang.jq` |
| Python libraries | pip / uv (Module 03) | `pip install requests` |
| JavaScript libraries | npm (Module 03) | `npm install axios` |

Package managers handle downloading, versions and updates. Prefer them to downloading random installers.

**Safety habits**
- Install from official sources only.
- Read a `curl … | sh` install command before you run it; know what it does.
- On client machines, install only what's approved. Many companies maintain an allowed-software list.

## Check yourself

1. You set `API_KEY=abc` (without `export`) and then run `python3 app.py`, which reads `os.environ["API_KEY"]`. What happens, and why?
2. Your colleague's script runs fine by hand but fails as a scheduled job with `node: command not found`. What's your first hypothesis?

Next: [Lesson 05 — Networking fundamentals](05-networking.md)
