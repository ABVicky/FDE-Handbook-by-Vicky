"""Exercise 03 — reference: a circuit breaker around a primary answerer. Run: python circuit_breaker.py"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
from admitflow.llm import Answer, ExtractiveAnswerer  # noqa: E402
from admitflow.rag import Retriever, load_corpus  # noqa: E402


class CircuitBreakerAnswerer:
    def __init__(self, primary, fallback, threshold=3, cooldown=60.0, clock=time.monotonic):
        self.primary, self.fallback = primary, fallback
        self.threshold, self.cooldown, self.clock = threshold, cooldown, clock
        self.failures, self.opened_at = 0, None

    @property
    def state(self):
        if self.opened_at is None:
            return "closed"
        return "half-open" if self.clock() - self.opened_at >= self.cooldown else "open"

    def answer(self, question, hits):
        if self.state == "open":
            return self.fallback.answer(question, hits)          # fail fast: don't wait for a timeout
        try:
            result = self.primary.answer(question, hits)
        except Exception:
            self.failures += 1
            if self.state == "half-open" or self.failures >= self.threshold:
                self.opened_at = self.clock()                    # (re)open
            return self.fallback.answer(question, hits)
        self.failures, self.opened_at = 0, None                  # success closes the circuit
        return result


class FlakyPrimary:
    def __init__(self):
        self.calls, self.down = 0, True

    def answer(self, question, hits):
        self.calls += 1
        if self.down:
            raise TimeoutError("provider timed out")
        return Answer("from the model", ["fees-2026#diploma-fees"], True, "claude")


if __name__ == "__main__":
    now = [0.0]
    retriever = Retriever(load_corpus(ROOT / "data" / "course_docs"))
    hits = retriever.search("Data Analytics fee")
    primary = FlakyPrimary()
    breaker = CircuitBreakerAnswerer(primary, ExtractiveAnswerer(), clock=lambda: now[0])

    for _ in range(3):
        assert breaker.answer("fee?", hits).engine == "offline"
    assert breaker.state == "open" and primary.calls == 3
    breaker.answer("fee?", hits)
    assert primary.calls == 3                                    # open: provider not called at all
    now[0] = 61
    assert breaker.state == "half-open"
    breaker.answer("fee?", hits)                                 # trial call fails → reopen
    assert breaker.state == "open" and primary.calls == 4
    now[0] = 125
    primary.down = False
    assert breaker.answer("fee?", hits).engine == "claude"       # trial succeeds → closed
    assert breaker.state == "closed" and breaker.failures == 0
    print("all checks passed")
