"""Evaluation for the course assistant (added in Module 08).

Each case in data/eval/assistant_eval.jsonl says what a good answer must do:
* `expected_chunk`: the section that should be retrieved and cited (null = the assistant should decline)
* `must_include`: facts the answer must contain (e.g. "1,800")
* `also_acceptable`: other sections that state the same fact (e.g. the FAQ)
* `must_not_include`: things it must never say (an outdated fee, a value an attacker tried to inject)

Metrics:
* retrieval@3: the expected section is among the top 3 retrieved
* correct: the case passes all its checks
* declined_correctly: for questions the documents can't answer, the assistant said so
* citation_valid: every citation refers to a retrieved section (enforced in code, so should be 100%)
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .llm import Answerer
from .rag import Retriever


@dataclass
class CaseResult:
    case_id: str
    category: str
    question: str
    passed: bool
    retrieved_expected: bool
    answered: bool
    answer: str
    reasons: List[str] = field(default_factory=list)


def load_cases(path: Path) -> List[Dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def run_case(case: Dict, retriever: Retriever, answerer: Answerer, k: int = 3) -> CaseResult:
    hits = retriever.search(case["question"], k=k)
    answer = answerer.answer(case["question"], hits)
    retrieved = [h.chunk.chunk_id for h in hits]
    reasons = []

    expected = case["expected_chunk"]
    if expected:
        if not answer.answered:
            reasons.append("declined an answerable question")
        acceptable = {expected, *case.get("also_acceptable", [])}   # the same fact can live in two documents
        if not acceptable & set(answer.citations):
            reasons.append(f"did not cite {expected}")
        for fact in case["must_include"]:
            if fact.lower() not in answer.text.lower():
                reasons.append(f"missing '{fact}'")
    elif case["category"] in ("unanswerable", "injection") and answer.answered:
        reasons.append("answered a question the documents don't cover")
    for bad in case.get("must_not_include", []):
        if bad.lower() in answer.text.lower():
            reasons.append(f"said '{bad.strip()}'")
    if not set(answer.citations) <= set(retrieved):
        reasons.append("cited a section that wasn't retrieved")

    return CaseResult(case["id"], case["category"], case["question"], not reasons,
                      bool(expected) and bool({expected, *case.get("also_acceptable", [])} & set(retrieved)), answer.answered, answer.text, reasons)


def evaluate(cases: List[Dict], retriever: Retriever, answerer: Answerer) -> Dict:
    start = time.perf_counter()
    results = [run_case(c, retriever, answerer) for c in cases]
    answerable = [r for r, c in zip(results, cases) if c["expected_chunk"]]
    must_decline = [r for r, c in zip(results, cases) if c["category"] in ("unanswerable", "injection") and not c["expected_chunk"]]
    by_category: Dict[str, List[int]] = {}
    for r in results:
        by_category.setdefault(r.category, [0, 0])
        by_category[r.category][0] += 1
        by_category[r.category][1] += r.passed
    return {
        "cases": len(results),
        "correct": round(sum(r.passed for r in results) / len(results), 3),
        "retrieval_at_3": round(sum(r.retrieved_expected for r in answerable) / len(answerable), 3),
        "declined_correctly": round(sum(not r.answered for r in must_decline) / max(len(must_decline), 1), 3),
        "by_category": {k: f"{p}/{n}" for k, (n, p) in sorted(by_category.items())},
        "seconds": round(time.perf_counter() - start, 2),
        "failures": [{"id": r.case_id, "question": r.question, "reasons": r.reasons, "answer": r.answer[:200]}
                     for r in results if not r.passed],
    }
