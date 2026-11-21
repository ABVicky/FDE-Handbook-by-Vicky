# Lesson 06 — Neural networks, transformers and embeddings (intuition)

**Time:** ~3 hours · **Core** (intuition) / *Stretch* (hands-on with PyTorch)

## Why this matters

You won't train large neural networks as an FDE. You'll use them through APIs (Module 08). But you need enough intuition to choose models sensibly, explain limitations to clients, and understand **embeddings**, the foundation of AI search.

## Neural networks in one paragraph

A neural network is layers of simple units. Each takes a weighted sum of its inputs and applies a non-linear function. Training adjusts millions or billions of weights by **gradient descent**: nudge every weight slightly in the direction that reduces the error, over and over, on many examples. Deep networks learn useful intermediate representations by themselves (edges → shapes → objects in images), which is why they dominate on images, audio and text, where hand-made features are hard.

For **tabular business data** like AdmitFlow's, gradient-boosted trees and logistic regression usually match or beat neural networks with far less effort.

## Transformers and language models

**Transformers** (2017) are the architecture behind modern language models. The key idea, **attention**, lets every word in a passage look at every other word to work out its meaning in context ("bank" near "river" vs. near "loan").

A **large language model** is a transformer trained to predict the next token on enormous amounts of text, then further trained to follow instructions. That's why it can answer questions, summarize and write code, and also why it can produce fluent, confident text that's **wrong** (hallucination): it generates plausible continuations, not verified facts. Module 08 is largely about controlling that.

## Embeddings: meaning as numbers

An **embedding** turns a piece of text into a vector, a list of numbers, such that **similar meanings are close together**.

```
"How much does the Data Analytics course cost?"  → [0.12, -0.03, 0.88, …]   ┐ close
"What are the fees for Data Analytics?"          → [0.10, -0.01, 0.85, …]   ┘
"Where is the North campus?"                     → [-0.40, 0.67, 0.02, …]     far
```

Closeness is usually measured with **cosine similarity** (1 = same direction, 0 = unrelated).

### Words vs. meaning

[Exercise 04](../exercises/04-similarity.md) uses **TF-IDF**, which represents text by its *words*, to match questions to an FAQ. It works when words overlap ("instalments" ↔ "instalments"), but it fails on:
- **Different word forms:** "instalment" vs "instalments" are different tokens unless you stem them
- **Different words, same meaning:** "will I get a job afterwards?" shares no words with "Is there a placement guarantee?", so it scores 0.0

Embedding models, trained on huge text collections, place both near each other because they *mean* similar things. That's the basis of **semantic search** and **retrieval-augmented generation (RAG)** in Module 08.

## Hugging Face, briefly

[Hugging Face](https://huggingface.co/) hosts thousands of open models and datasets. With the `sentence-transformers` library, you can create embeddings locally:

```python
from sentence_transformers import SentenceTransformer   # pip install sentence-transformers (downloads a model)
model = SentenceTransformer("all-MiniLM-L6-v2")
vectors = model.encode(["What are the fees?", "How much does it cost?"])
```

Useful when data mustn't leave the client's environment. Module 08 compares hosted and local options.

*Stretch:* work through the PyTorch "Learn the Basics" tutorial and train a tiny network on the historical leads. Compare it with logistic regression: you'll likely find no gain, which is itself a useful result.

## Check yourself

Explain to a non-technical person, in three sentences each: (1) why a language model can state a wrong fee confidently; (2) what an embedding is, using an analogy.

Next: [Lesson 07 — Responsible ML](07-responsible-ml.md)
