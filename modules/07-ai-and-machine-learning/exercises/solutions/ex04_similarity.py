"""Exercise 04 — reference: find the most similar FAQ question (a first step towards RAG in Module 08).

TF-IDF turns text into vectors of word weights; cosine similarity compares them.
It matches words, not meaning: Module 08's embeddings fix that.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FAQ = {
    "What are the fees for Data Analytics?": "The Data Analytics diploma costs 1,800 per term (2026).",
    "Do you offer evening classes?": "Yes: Accounting and Digital Marketing run evening batches, 6–9pm.",
    "Is there a placement guarantee?": "We offer placement assistance, not a guarantee. 78% found jobs within 6 months (2025).",
    "Can I pay fees in instalments?": "Yes, in three instalments per term with no extra charge.",
    "Where is the North campus?": "North campus is at 12 Park Road, next to the metro station.",
}

vectorizer = TfidfVectorizer(stop_words="english")
faq_vectors = vectorizer.fit_transform(FAQ.keys())


def best_match(question: str):
    similarities = cosine_similarity(vectorizer.transform([question]), faq_vectors)[0]
    best = similarities.argmax()
    return list(FAQ)[best], round(float(similarities[best]), 2)


tests = [
    ("how much is the data analytics course", "What are the fees for Data Analytics?"),
    ("can I study in the evening after work", "Do you offer evening classes?"),
    ("can I pay in instalments?", "Can I pay fees in instalments?"),
]
for question, expected in tests:
    match, score = best_match(question)
    print(f"{question!r:45} → {match!r} ({score})")
    assert match == expected

# A limitation worth seeing: no shared words, so TF-IDF can't match it, even though the meaning is close.
print(best_match("will I get a job afterwards?"))
