# Setting up your development environment

**Time:** ~1 hour · You'll reuse this setup for the whole handbook.

You need five things: a **terminal**, a **shell**, **Git**, **Python 3**, and a **code editor**. Follow the section for your operating system, then run the [final check](#final-check).

---

## macOS

1. **Terminal:** open *Terminal* (Applications → Utilities). The default shell is **zsh**, which is fine.
2. **Command-line developer tools** (includes Git):
   ```bash
   xcode-select --install
   ```
3. **Homebrew** (a package manager): follow the instructions at https://brew.sh. Read the command before you paste it; that's a good habit with any install script.
4. **Python 3:**
   ```bash
   brew install python
   ```
5. **VS Code:** download from https://code.visualstudio.com, then in VS Code open the Command Palette (⇧⌘P) → *Shell Command: Install 'code' command in PATH*.

## Ubuntu / Debian Linux

```bash
sudo apt update
```

```bash
sudo apt install -y git python3 python3-venv python3-pip curl dnsutils
```

Install VS Code from https://code.visualstudio.com (the `.deb` package), or use your preferred editor.

## Windows

You'll do your work inside **WSL** (a real Linux system running inside Windows). This keeps every command in the handbook identical for everyone.

1. Open **PowerShell as Administrator** and run:
   ```powershell
   wsl --install
   ```
   Restart when asked. This installs Ubuntu by default.
2. Open **Ubuntu** from the Start menu, create a Linux username and password.
3. Inside Ubuntu, follow the **Ubuntu / Debian Linux** steps above.
4. Install **VS Code** on Windows, then install the **WSL** extension. From the Ubuntu terminal, `code .` opens VS Code connected to Linux.

> Keep your project files inside the Linux file system (e.g. `~/projects`), not under `/mnt/c/...`. It's much faster and avoids permission oddities.

---

## Configure Git (all systems)

```bash
git config --global user.name "Your Name"
```

```bash
git config --global user.email "you@example.com"
```

Use the email address you'll use on GitHub. Create a free GitHub account if you don't have one.

## Get the handbook

```bash
mkdir -p ~/projects && cd ~/projects
```

```bash
git clone https://github.com/<your-username>/fde-handbook.git
```

(Fork the repository on GitHub first so you have your own copy to push work to. Module 03 covers Git properly.)

---

## Final check

Run each command. Every one should print a version or a path, not "command not found".

```bash
echo $SHELL
```

```bash
git --version
```

```bash
python3 --version
```

```bash
curl --version | head -1
```

```bash
code --version | head -1
```

```bash
which dig || which nslookup
```

- [ ] All six commands worked
- [ ] Python is 3.9 or newer
- [ ] You can open the handbook folder in VS Code with `code .`

**Stuck?** Copy the exact error message and search for it. That's a core FDE skill, and [Lesson 07](lessons/07-troubleshooting.md) covers it. If you're still stuck, open an issue with the label `setup-help`, including your OS, the command and the full error.
