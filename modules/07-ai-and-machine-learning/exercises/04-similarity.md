# Exercise 04 — Find the most similar question

Given a small FAQ (in the solution file), use scikit-learn's `TfidfVectorizer` and cosine similarity to return the FAQ question most similar to a student's question.

1. Make it match "how much is the data analytics course", "can I study in the evening after work" and "can I pay in instalments?" correctly.
2. Try "instalment payment possible?". Why does it fail when "can I pay in instalments?" works? (Hint: "instalment" and "instalments" are different tokens.)
3. Try "will I get a job afterwards?". Why does it score 0? What kind of representation would fix it? (Module 08: embeddings.)
