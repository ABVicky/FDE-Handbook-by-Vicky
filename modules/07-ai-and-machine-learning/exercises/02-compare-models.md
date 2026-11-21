# Exercise 02 — Compare models honestly

Using only enquiry-time features (source, course, extra channels, has email, has phone, out of hours), train on 2024 and test on 2025:

1. A baseline: each source's 2024 conversion rate
2. Logistic regression
3. Gradient boosting (shallow trees)

Report ROC AUC and precision in the top 20% for each, next to the test base rate. Then answer: does the more complex model help? What does that tell you about where the signal is?
