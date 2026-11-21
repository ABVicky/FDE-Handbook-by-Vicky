# Exercise 03 — A tool-use loop, tested without the network

1. Implement the manual tool loop from Lesson 05 with two tools: `search_course_info(query)` and `get_lead(lead_id)`.
2. `get_lead` must refuse leads assigned to another counsellor, enforced **in code**.
3. Build a scripted fake client that returns pre-written responses (a `tool_use` turn, then a final text turn), and test:
   - a search happens and its result is sent back as a `tool_result` with the right `tool_use_id`
   - a forbidden `get_lead` returns an `is_error` result rather than crashing or leaking data
   - the loop stops after a maximum number of steps
4. *(Optional, costs money)* Run it against the real API with your credentials and compare.
