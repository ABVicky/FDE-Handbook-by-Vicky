# Lesson 03 — Control flow: if, for, while

**Time:** ~3 hours · **Core**

## if / elif / else

```python
hours_waiting = 30

if hours_waiting > 48:
    priority = "urgent"
elif hours_waiting > 24:
    priority = "high"
else:
    priority = "normal"
```

Indentation (4 spaces) defines the block. Python has no braces.

## for loops: do something for each item

```python
sources = ["website", "ad", "phone"]
for source in sources:
    print(source.upper())

for i in range(3):            # 0, 1, 2
    print(i)

for number, source in enumerate(sources, start=1):
    print(number, source)     # 1 website, 2 ad, 3 phone
```

Looping over two lists together:

```python
names = ["Grace", "Omar"]
courses = ["Accounting", "Web Development"]
for name, course in zip(names, courses):
    print(f"{name} → {course}")
```

## while loops: repeat until a condition changes

```python
attempts = 0
while attempts < 3:
    attempts += 1
    print(f"Attempt {attempts}")
```

Use `while` when you don't know in advance how many times you'll loop (e.g. retrying a network call). Make sure the condition can become false, or the loop runs forever (stop it with <kbd>Ctrl</kbd>+<kbd>C</kbd>).

## break and continue

```python
for lead in ["ok", "ok", "STOP", "never reached"]:
    if lead == "STOP":
        break        # leave the loop
    print(lead)

for phone in ["+12025550101", "", "+12025550102"]:
    if not phone:
        continue     # skip to the next item
    print("calling", phone)
```

## A small real example

Count how many leads waited more than 24 hours:

```python
waits = [2, 30, 5, 49, 26, 1]
late = 0
for hours in waits:
    if hours > 24:
        late += 1
print(f"{late} of {len(waits)} waited over 24h")   # 3 of 6 waited over 24h
```

Lesson 05 shows shorter ways to write this (`sum(1 for h in waits if h > 24)`), but the loop version is always fine, and often clearer.

## Check yourself

Write a loop that prints the numbers 1–30, but prints `"follow up"` instead of the number for every multiple of 7, and stops entirely if it reaches 25.

Next: [Lesson 04 — Functions](04-functions.md)
