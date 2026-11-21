# Lesson 04 — Embeddings and vector search

**Time:** ~4 hours · **Core**

## Why

Keyword search can't connect "will I get a job afterwards?" to "Is there a placement guarantee?" (Module 07, Exercise 04). **Embeddings** represent meaning as vectors, so semantically similar text lands close together, across different words and even different languages.

## How vector search works

1. **Index time:** embed every chunk → store `(chunk_id, vector, metadata)`.
2. **Query time:** embed the question → find the chunks whose vectors are nearest (cosine similarity) → filter by metadata → top k.

```python
import numpy as np

def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

For a few thousand chunks, a brute-force scan in numpy is fast enough. Beyond that, vector indexes (HNSW, IVF) trade a little accuracy for big speed gains.

## Where embeddings come from

Anthropic doesn't offer an embedding model; use a dedicated one:

| Option | Notes |
| --- | --- |
| Hosted embedding APIs (e.g. Voyage AI, OpenAI, Cohere, Google) | Strong quality; data leaves the client's environment |
| Open models via `sentence-transformers` (e.g. multilingual MiniLM / E5 / BGE families) | Run locally or inside the client's network; free per call |
| Cloud-native (Bedrock, Vertex AI, Azure) | Data stays in the client's chosen cloud |

Choose by: quality **on your evaluation set**, languages, data-residency rules, cost and latency. Re-embed everything if you change models: vectors from different models aren't comparable.

```python
from sentence_transformers import SentenceTransformer   # pip install sentence-transformers

model = SentenceTransformer("all-MiniLM-L6-v2")          # small, English; downloads once
vectors = model.encode([chunk.text for chunk in chunks], normalize_embeddings=True)
```

## Storing vectors: pgvector first

AdmitFlow already runs PostgreSQL. The `pgvector` extension adds a vector column type and similarity search, so no new database is needed:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE doc_chunks (
    chunk_id       TEXT PRIMARY KEY,
    doc            TEXT NOT NULL,
    section        TEXT NOT NULL,
    text           TEXT NOT NULL,
    effective_from DATE NOT NULL,
    superseded     BOOLEAN NOT NULL DEFAULT FALSE,
    embedding      vector(384)                 -- dimension of your embedding model
);

CREATE INDEX ON doc_chunks USING hnsw (embedding vector_cosine_ops);

-- top 3 current chunks for a question vector :q
SELECT chunk_id, text, 1 - (embedding <=> :q) AS similarity
FROM doc_chunks
WHERE NOT superseded
ORDER BY embedding <=> :q
LIMIT 3;
```

(`<=>` is cosine distance.) Metadata filters and vector search happen in one query, with the same backups, permissions and operations as the rest of the data. Dedicated vector databases (Qdrant, Pinecone, Weaviate, Milvus) make sense at much larger scale or with specialized needs.

## Hybrid search

Keyword and vector search fail differently: keywords catch exact terms (course codes, "1,800", names), vectors catch meaning. Combine them, e.g. with **reciprocal rank fusion**:

```python
def rrf(rankings, k=60):
    """rankings: lists of chunk_ids, best first. Returns chunk_ids ordered by fused score."""
    scores = {}
    for ranking in rankings:
        for position, chunk_id in enumerate(ranking):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + position + 1)
    return sorted(scores, key=scores.get, reverse=True)

fused = rrf([bm25_ids, vector_ids])[:3]
```

## When AdmitFlow should add embeddings

Not yet: with ~25 sections, BM25 plus an FAQ reaches retrieval@3 = 1.0 on the evaluation. Add embeddings when:
- the evaluation shows paraphrase misses that documents can't reasonably fix
- the corpus grows (hundreds of documents) or questions come in several languages
- the client's data rules allow the chosen embedding model

And **measure** the switch on the same evaluation set. Embeddings aren't automatically better; they're different.

## Check yourself

Do [Exercise 02](../exercises/02-hybrid-search.md): add a second, meaning-based ranking (any embedding model, or the TF-IDF stand-in provided), fuse it with BM25 using RRF, and compare retrieval@3 on the evaluation set, including on the paraphrased cases.

Next: [Lesson 05 — Tool use, workflows and agents](05-tools-and-agents.md)
