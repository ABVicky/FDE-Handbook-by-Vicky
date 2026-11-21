# Exercise 02 — Hybrid search with reciprocal rank fusion

1. Implement `rrf(rankings, k=60)` (Lesson 04).
2. Produce two rankings per question: AdmitFlow's BM25 and a second, meaning-oriented ranking (a real embedding model if you can; otherwise the TF-IDF character n-gram stand-in in the solution).
3. Compare retrieval@3 for BM25, vector and hybrid on the evaluation set, **with and without** the FAQ document.
4. Write three sentences: would you add embeddings to AdmitFlow now? What evidence would change your mind?
