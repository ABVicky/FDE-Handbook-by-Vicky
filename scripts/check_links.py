"""Check every relative Markdown link and #anchor in the handbook. Exit 1 if any are broken."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"templates/module-template.md"}  # contains placeholder links by design
LINK = re.compile(r"\]\(([^)\s]+)\)")


def slug(heading: str) -> str:
    heading = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return heading.replace(" ", "-")


def anchors(path: Path) -> set:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # headings inside code blocks don't count
    return {slug(h) for h in re.findall(r"^#+\s+(.*)$", text, re.M)}


def main() -> int:
    problems = []
    files = [p for p in ROOT.rglob("*.md") if "node_modules" not in p.parts]
    for md in files:
        rel = md.relative_to(ROOT).as_posix()
        if rel in SKIP:
            continue
        for link in LINK.findall(md.read_text(encoding="utf-8")):
            if link.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            path, _, anchor = link.partition("#")
            target = (md.parent / path).resolve() if path else md
            if not target.exists():
                if target.name != "LICENSE":
                    problems.append(f"{rel}: missing {link}")
                continue
            if anchor and target.suffix == ".md" and anchor not in anchors(target):
                problems.append(f"{rel}: missing anchor {link}")
    for problem in problems:
        print(problem)
    print(f"{len(files)} files checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
