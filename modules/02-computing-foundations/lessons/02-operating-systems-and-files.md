# Lesson 02 — Operating systems, files and permissions

**Time:** ~3 hours · **Core**

## Why this matters

Most servers you'll touch at client sites run **Linux**. Your laptop might run macOS or Windows. Knowing what's the same and what's different, especially around files and permissions, prevents hours of confusion.

## What an operating system does

The OS is the manager between programs and hardware:

- **Runs processes** and shares the CPU between them
- **Manages memory** so programs don't overwrite each other
- **Manages files** on storage
- **Controls access**: users, groups and permissions
- **Handles devices and networking**

## The three you'll meet

| | Linux | macOS | Windows |
| --- | --- | --- | --- |
| Where you'll see it | Almost all servers, containers, cloud | Many developer laptops | Many corporate laptops and some servers |
| Default shell | bash | zsh | PowerShell (use WSL for this handbook) |
| Path separator | `/` | `/` | `\` |
| Root of file system | `/` | `/` | `C:\` |
| Home folder | `/home/you` | `/Users/you` | `C:\Users\you` |
| Case-sensitive file names? | Yes | Usually no | No |
| Line endings in text files | LF | LF | CRLF |

Two gotchas worth memorizing:
1. **Case sensitivity:** `Leads.csv` and `leads.csv` are *different files* on Linux. Code that works on your Mac can fail on the server.
2. **Line endings:** files edited on Windows may end lines with `\r\n`. Linux tools may then see a stray `\r` at the end of each line (you'll hit this in the build task).

## Files, folders and paths

The file system is a tree, starting at the root `/`:

```
/
├── home/
│   └── priya/
│       └── projects/
│           └── admitflow/
│               └── data/leads_sample.csv
├── etc/          ← system configuration
├── var/log/      ← log files
└── tmp/          ← temporary files
```

- **Absolute path:** starts from the root: `/home/priya/projects/admitflow/data/leads_sample.csv`
- **Relative path:** starts from where you are now: `data/leads_sample.csv`
- Special names: `.` (this folder), `..` (parent folder), `~` (your home folder)

## Users and permissions

Every file has an **owner**, a **group**, and **permissions** for three audiences: the owner (**u**ser), the **g**roup, and **o**thers.

```bash
ls -l start.sh
```
```
-rw-r--r--  1 priya  staff  182 Nov 21 10:00 start.sh
```

Read the first column in groups:

```
-   rw-   r--   r--
│   │     │     └── others: read
│   │     └──────── group:  read
│   └────────────── owner:  read, write
└────────────────── type: - file, d directory, l link
```

| Letter | On a file | On a directory |
| --- | --- | --- |
| `r` read | View contents | List contents |
| `w` write | Change contents | Create/delete files inside |
| `x` execute | Run it as a program | Enter it (`cd`) |

Changing permissions:

```bash
chmod +x start.sh      # add execute for everyone
chmod u+x start.sh     # add execute for the owner only
chmod 600 secrets.env  # owner read+write, nobody else anything
```

The number form: `r=4, w=2, x=1`, added up per audience. `755` = owner `rwx`, group `r-x`, others `r-x`. `600` = owner `rw-`, others nothing. That's a sensible setting for files holding secrets.

## The superuser

`root` (Linux/macOS) can do anything. `sudo` runs a single command as root:

```bash
sudo apt install curl
```

**FDE rule:** on a client machine, never use `sudo` casually. You may not have the right, it may be logged and audited, and it's the fastest way to break something you can't fix. If you think you need root, ask first and explain why.

## Check yourself

1. What does `chmod 640 report.csv` allow, and for whom?
2. A script works on your Mac but on the Linux server fails with `No such file or directory: Data/leads.csv`. The folder is called `data`. Why did it work on your Mac?

Next: [Lesson 03 — The command line](03-command-line.md)
