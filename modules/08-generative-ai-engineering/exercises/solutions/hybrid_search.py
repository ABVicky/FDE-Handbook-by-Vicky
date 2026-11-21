"""Exercise 02 — reference: fuse BM25 with a meaning-style ranking using reciprocal rank fusion.

The "vector" ranking here uses TF-IDF character n-grams from scikit-learn as a free, offline stand-in
for an embedding model (it tolerates word-form differences, but doesn't truly understand meaning).
Swap `vector_rank` for a real embedding model (e.g. sentence-transformers) and re-run the comparison.

Run: python hybrid_search.py   (needs admitflow installed, plus scikit-learn)
"""
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[4] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
from admitflow.evals import load_cases  # noqa: E402
from admitflow.rag import Retriever, load_corpus  # noqa: E402

chunks = [c for c in load_corpus(ROOT / "data" / "course_docs") if not c.superseded]
retriever = Retriever(chunks)
vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
matrix = vectorizer.fit_transform(c.text for c in chunks)


def bm25_rank(question, n=10):
    return [h.chunk.chunk_id for h in retriever.search(question, k=n)]


def vector_rank(question, n=10):
    scores = cosine_similarity(vectorizer.transform([question]), matrix)[0]
    return [chunks[i].chunk_id for i in scores.argsort()[::-1][:n]]


def rrf(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for position, chunk_id in enumerate(ranking):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + position + 1)
    return sorted(scores, key=scores.get, reverse=True)


all_cases = [c for c in load_cases(ROOT / "data" / "eval" / "assistant_eval.jsonl") if c["expected_chunk"]]


def compare(corpus, cases, label):
    global chunks, retriever, matrix
    chunks = corpus
    retriever = Retriever(chunks)
    matrix = vectorizer.fit_transform(c.text for c in chunks)
    methods = {
        "bm25": lambda q: bm25_rank(q)[:3],
        "vector (stand-in)": lambda q: vector_rank(q)[:3],
        "hybrid (RRF)": lambda q: rrf([bm25_rank(q), vector_rank(q)])[:3],
    }
    print(f"\n{label}: retrieval@3 on {len(cases)} answerable cases")
    results = {}
    for name, rank in methods.items():
        hits = sum(bool({c["expected_chunk"], *c.get("also_acceptable", [])} & set(rank(c["question"]))) for c in cases)
        results[name] = round(hits / len(cases), 3)
        print(f"  {name:<18} {results[name]:.3f}")
    return results


full = compare(chunks, all_cases, "With the FAQ document")
# Without the FAQ: the paraphrased questions must be answered from the original documents.
no_faq_chunks = [c for c in chunks if c.doc != "faq"]
no_faq_cases = []
for case in all_cases:
    options = [x for x in [case["expected_chunk"], *case.get("also_acceptable", [])] if not x.startswith("faq#")]
    if options:
        no_faq_cases.append({**case, "expected_chunk": options[0], "also_acceptable": options[1:]})
without = compare(no_faq_chunks, no_faq_cases, "Without the FAQ document")

assert full["bm25"] == 1.0
print("\nWith the FAQ, keyword search is already perfect here. Without it, one paraphrased question is missed,")
print("and the character n-gram stand-in doesn't fix it: it matches spelling, not meaning. Swap in a real")
print("embedding model for `vector_rank` and see whether hybrid search closes the gap. Always measure.")
