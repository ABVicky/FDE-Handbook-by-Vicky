# Exercise 02 — Ask the data questions with pipelines

The Head of Admissions has questions. Answer each with **one pipeline** on `leads_sample.csv`. Write down the command *and* the answer.

The columns are:

```
enquiry_id,received_at,name,phone,email,course,source
```

1. How many lines does the file have? How many of those are actual leads? (Look carefully. There are surprises.)
2. How many enquiries arrived in the first week of September (1st–7th)?
3. Which names were written as "Last, First" in quotes? How many are there?
4. How many leads have **no phone number**?
5. How many enquiries were there **per course**? Try the obvious approach first: `cut -d, -f6`. Is the result right? Why not? Then fix it.
6. Which course is most popular among **WhatsApp** enquiries?

## Reflect

Write two or three sentences: what did question 5 teach you about using simple text tools on CSV data? (You'll handle CSV properly with Python in Module 03.)
