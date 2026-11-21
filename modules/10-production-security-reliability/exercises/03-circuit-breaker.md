# Exercise 03 — A circuit breaker around the LLM provider

When the LLM provider is down, every question waits for a timeout before falling back. Wrap the answerer in a **circuit breaker**:
- **Closed** (normal): calls go through; count consecutive failures
- After **3 consecutive failures** → **open** for 60 seconds: skip the provider entirely and use the offline answerer immediately
- After 60 seconds → **half-open**: try one call; success closes the circuit, failure reopens it

Implement `CircuitBreakerAnswerer(primary, fallback, threshold=3, cooldown=60, clock=time.monotonic)` and test every transition with a fake clock.
