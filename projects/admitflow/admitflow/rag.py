"""Retrieval for the course assistant (added in Module 08).

    course_docs/*.md  →  chunks (one per section, with metadata)  →  BM25 index  →  top-k chunks

Design notes (see docs/adr/005-course-assistant.md):
* Chunk by **section**, not by fixed character counts: a section is one idea, with its heading for context.
* Keep **metadata** with every chunk (document, section, effective date, superseded flag) so retrieval
  can filter out outdated documents. Ignoring this is Module 08's break & fix.
* BM25 keyword search is pure Python, fast and transparent. An embedding model can be added
  alongside it (hybrid search) without changing anything else: see `Retriever.search`.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Chunk:
    chunk_id: str            # "fees-2026#diploma-fees"
    doc: str                 # "fees-2026"
    title: str               # "Fee schedule 2026–27"
    section: str             # "Diploma fees"
    text: str                # the section body, prefixed with title and section
    effective_from: date
    superseded: bool = False


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _front_matter(raw: str):
    """Parse a simple `---\\nkey: value\\n---` header. Returns (metadata, body)."""
    meta: Dict[str, str] = {}
    if raw.startswith("---"):
        header, _, body = raw[3:].partition("\n---")
        for line in header.strip().splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
        return meta, body
    return meta, raw


def chunk_document(path: Path) -> List[Chunk]:
    meta, body = _front_matter(Path(path).read_text(encoding="utf-8"))
    doc = Path(path).stem
    title = meta.get("title", doc)
    effective = date.fromisoformat(meta.get("effective_from", "1970-01-01"))
    superseded = meta.get("superseded", "false").lower() == "true"

    chunks: List[Chunk] = []
    intro: List[str] = []
    section, lines = None, []

    def flush():
        if section and any(line.strip() for line in lines):
            text = f"{title} — {section}\n" + "\n".join(lines).strip()
            chunks.append(Chunk(f"{doc}#{_slug(section)}", doc, title, section, text, effective, superseded))

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            section, lines = line[3:].strip(), []
        elif line.startswith("# "):
            continue
        elif section is None:
            intro.append(line)
        else:
            lines.append(line)
    flush()
    # General statements before the first section ("All fees are per term") apply to every section
    intro_text = " ".join(l.strip() for l in intro if l.strip())
    if intro_text:
        for chunk in chunks:
            chunk.text = chunk.text.replace("\n", f"\n{intro_text}\n", 1)
    return chunks


def load_corpus(folder: Path) -> List[Chunk]:
    return [chunk for path in sorted(Path(folder).glob("*.md")) for chunk in chunk_document(path)]


# -- tokenizing --------------------------------------------------------------------------

STOPWORDS = set(
    "a an and are as at be by can do does for from have how i in is it me my of on or the there "
    "this to what when where which who will with you your "
    # generic question words that say nothing about the topic
    "any also get give just know like many much need offer please tell want".split()
)


def _stem(word: str) -> str:
    """A deliberately tiny stemmer: instalments → instalment, classes → class, fees → fee."""
    if word.endswith(("us", "ss", "is")):      # campus, class, analysis: not plurals
        return word
    for suffix in ("ies", "es", "s"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            if suffix == "ies":
                return word[:-3] + "y"
            if suffix == "es" and word[-3] in "sxz":
                return word[:-2]
            return word[:-1]
    return word


def tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-z0-9]+", text.lower().replace(",", ""))
    return [_stem(w) for w in words if w not in STOPWORDS]


# Query expansion: students ask "how much…?" but documents say "fee". A tiny, explicit synonym list
# beats nothing; embeddings (Lesson 04) handle this more generally.
EXPANSIONS = {
    "how much": "fee", "cost": "fee", "price": "fee", "pay": "fee",
    "timing": "class", "schedule": "class", "address": "campus", "located": "campus",
    "phone": "call", "learn": "covering", "cover": "covering", "topic": "covering", "how long": "month year",
}


def expand_query(query: str) -> str:
    lowered = query.lower()
    extra = [target for phrase, target in EXPANSIONS.items() if phrase in lowered]
    return query + (" " + " ".join(extra) if extra else "")


# -- BM25 ---------------------------------------------------------------------------------

@dataclass
class Hit:
    chunk: Chunk
    score: float


@dataclass
class Retriever:
    chunks: List[Chunk]
    k1: float = 1.5
    b: float = 0.75
    _docs: List[Counter] = field(default_factory=list, init=False)
    _idf: Dict[str, float] = field(default_factory=dict, init=False)
    _avg_len: float = field(default=0.0, init=False)

    def __post_init__(self):
        self._docs = [Counter(tokenize(c.text)) for c in self.chunks]
        n = len(self._docs)
        df = Counter(term for doc in self._docs for term in doc)
        self._idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self._avg_len = sum(sum(d.values()) for d in self._docs) / max(n, 1)

    def _bm25(self, query_terms: Iterable[str], doc: Counter) -> float:
        length = sum(doc.values())
        score = 0.0
        for term in query_terms:
            tf = doc.get(term, 0)
            if tf:
                score += self._idf[term] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * length / self._avg_len))
        return score

    def search(self, query: str, k: int = 3, *, as_of: Optional[date] = None,
               include_superseded: bool = False) -> List[Hit]:
        """Top-k chunks. Superseded documents, and documents not yet in effect on `as_of`, are excluded."""
        terms = set(tokenize(expand_query(query)))
        hits = []
        for chunk, doc in zip(self.chunks, self._docs):
            if chunk.superseded and not include_superseded:
                continue
            if as_of and chunk.effective_from > as_of:
                continue
            score = self._bm25(terms, doc)
            if score > 0:
                hits.append(Hit(chunk, round(score, 3)))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]
