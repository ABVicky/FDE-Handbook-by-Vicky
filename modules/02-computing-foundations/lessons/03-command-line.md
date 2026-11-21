# Lesson 03 — The command line

**Time:** ~5 hours (the longest lesson, so practise as you read) · **Core**

## Why this matters

The terminal is the one interface that works everywhere: your laptop, a client's server over SSH, a container, a cloud VM. It's also how you automate: anything you can type, you can put in a script.

## Terminal, shell, command

- **Terminal:** the window you type in.
- **Shell:** the program that reads your commands and runs them (bash, zsh).
- **Command:** a program plus its arguments: `ls -l data/`
  - `ls` is the program
  - `-l` is an **option** (flag) that changes its behaviour
  - `data/` is an **argument** (what to act on)

## Getting help

```bash
man ls          # the manual (press q to quit, / to search)
ls --help       # short help (on Linux; macOS often uses man)
```

And: copy the exact error into a search engine. Everyone does this.

## Moving around

| Command | Does |
| --- | --- |
| `pwd` | Print where you are |
| `ls` / `ls -la` | List files / including hidden ones, with details |
| `cd projects` | Go into a folder |
| `cd ..` | Go up one level |
| `cd ~` or `cd` | Go home |
| `cd -` | Go back to the previous folder |

**Tab completion:** type the first few letters and press <kbd>Tab</kbd>. It saves time and prevents typos. Press <kbd>↑</kbd> to recall previous commands, and <kbd>Ctrl</kbd>+<kbd>R</kbd> to search your history.

## Working with files

| Command | Does |
| --- | --- |
| `mkdir -p a/b/c` | Create folders (and parents) |
| `touch notes.md` | Create an empty file |
| `cp a.txt b.txt` | Copy |
| `mv a.txt b.txt` | Move or rename |
| `rm file.txt` | Delete a file (**no recycle bin!**) |
| `rm -r folder/` | Delete a folder and everything in it (**be careful**) |

⚠️ `rm` is permanent. Before running `rm -r` with a wildcard, run `ls` with the same pattern to see exactly what would be deleted.

## Reading files

| Command | Does |
| --- | --- |
| `cat file` | Print the whole file |
| `less file` | Scroll through it (q to quit) |
| `head -5 file` | First 5 lines |
| `tail -5 file` | Last 5 lines |
| `tail -f app.log` | Follow a log as it grows (Ctrl+C to stop) |
| `wc -l file` | Count lines |

## Searching

```bash
grep "Website" leads_sample.csv          # lines containing Website
grep -i "website" leads_sample.csv       # ignore case
grep -c -i "website" leads_sample.csv    # just count matching lines
grep -rn "ADMITFLOW" .                   # search all files below here, show line numbers
find . -name "*.csv"                     # find files by name
```

## Pipes and redirection: the superpower

Each command reads **input** and writes **output**. You can connect them.

| Symbol | Meaning | Example |
| --- | --- | --- |
| `\|` | Send output of one command into the next | `cat file \| grep x` |
| `>` | Write output to a file (overwrites!) | `ls > files.txt` |
| `>>` | Append output to a file | `echo "done" >> log.txt` |
| `2>` | Write **errors** to a file | `cmd 2> errors.txt` |
| `<` | Read input from a file | `wc -l < file` |

A real pipeline, step by step, on the AdmitFlow data:

```bash
cut -d, -f6 leads_sample.csv | sort | uniq -c | sort -rn
```

1. `cut -d, -f6`: take the 6th comma-separated field (the course)
2. `sort`: put identical values next to each other
3. `uniq -c`: collapse duplicates and count them
4. `sort -rn`: sort by count, highest first

Build pipelines **one step at a time**: run the first command, check the output, add the next.

*Note:* `cut` splits on every comma, even commas inside quoted values like `"Rao, Anita"`. That's a real problem with CSV files. The build task makes you deal with it.

## Processes

| Command | Does |
| --- | --- |
| `ps aux` | List all processes |
| `ps aux \| grep python` | Find Python processes |
| `top` (or `htop`) | Live view of CPU/memory use |
| `kill 4182` | Ask process 4182 to stop |
| `kill -9 4182` | Force it (last resort) |
| <kbd>Ctrl</kbd>+<kbd>C</kbd> | Stop the program running in this terminal |
| `command &` | Run in the background |

## Writing a small script

Put commands in a file to run them again later:

```bash
#!/usr/bin/env bash
# count_lines.sh — print how many lines each CSV in a folder has
set -euo pipefail

folder="${1:-.}"
for f in "$folder"/*.csv; do
  echo "$(wc -l < "$f") $f"
done
```

- The first line (the "shebang") says which program runs the script.
- `set -euo pipefail` stops the script on errors instead of carrying on silently. Use it in every script.
- `$1` is the first argument; `${1:-.}` means "or `.` if none was given".
- Always put variables in double quotes (`"$f"`), so file names with spaces don't break.

Make it executable and run it:

```bash
chmod +x count_lines.sh
```

```bash
./count_lines.sh ../../projects/admitflow/data
```

*Stretch:* learn `if`, `while`, functions and `case` in bash; read about `awk`, a small language for processing columns of text.

## Check yourself

Write a single pipeline that prints the **five busiest days** (most enquiries) in `leads_sample.csv`. Hint: `received_at` is field 2 and looks like `2026-09-01 10:55`; `cut -d' ' -f1` keeps only the text before the first space. (Answer in [exercises/solutions](../exercises/solutions/README.md#lesson-03-check-yourself).)

Next: [Lesson 04 — Environment variables, PATH and installing software](04-environment-and-path.md)
