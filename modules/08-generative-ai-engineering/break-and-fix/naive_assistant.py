"""A first-version course assistant, built in an afternoon for a demo. It "worked great" in the demo.

Usage: python naive_assistant.py "How much is the Data Analytics course?"
Standard library only.
"""
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[3] / "projects" / "admitflow" / "data" / "course_docs"
CHUNK_SIZE = 400


def load_chunks():
    chunks = []
    for path in sorted(DOCS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for start in range(0, len(text), CHUNK_SIZE):            # fixed-size chunks
            chunks.append(text[start:start + CHUNK_SIZE])
    return chunks


def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def answer(question):
    chunks = load_chunks()
    best = max(chunks, key=lambda chunk: len(words(question) & words(chunk)))   # top-1 by word overlap
    return f"Here's what I found:\n{best.strip()}"


if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:]) or "How much is the Data Analytics course?"))
