# Lesson 18 — JavaScript essentials

**Time:** ~5 hours · **Core**

## Why this matters

Every web dashboard you build (Module 04) runs JavaScript in the browser. Many client systems, webhooks and automation tools also use JavaScript or TypeScript on the server (Node.js). You don't need to be a JavaScript expert yet, but you must be able to read it, write small programs, and call APIs with it.

You already know how to program. Most concepts carry over from Python; this lesson focuses on the differences.

## Running JavaScript

- **In the browser:** open Developer Tools (<kbd>F12</kbd>) → *Console*.
- **With Node.js** (install from https://nodejs.org, LTS version):
  ```bash
  node --version
  ```
  ```bash
  node hello.js
  ```

## Python → JavaScript cheat sheet

| Python | JavaScript |
| --- | --- |
| `name = "Zoë"` | `const name = "Zoë";` (or `let` if it will change) |
| `None` | `null` (and `undefined` for "never set") |
| `True` / `False` | `true` / `false` |
| `f"Hi {name}"` | `` `Hi ${name}` `` (backticks) |
| `print(x)` | `console.log(x)` |
| `len(items)` | `items.length` |
| `items.append(x)` | `items.push(x)` |
| `dict` `{"a": 1}` | object `{ a: 1 }` |
| `if x == 1:` | `if (x === 1) { … }` |
| `for x in items:` | `for (const x of items) { … }` |
| `def f(a, b=2):` | `function f(a, b = 2) { … }` or `const f = (a, b = 2) => …` |
| `[x * 2 for x in xs if x > 1]` | `xs.filter(x => x > 1).map(x => x * 2)` |
| `import json` / `json.loads(s)` | `JSON.parse(s)` (built in) |

## Gotchas for Python programmers

```javascript
// Always use === (strict equality). == does surprising type conversions.
0 == "0";     // true  😬
0 === "0";    // false ✅

// const means the variable can't be reassigned, not that the object can't change
const lead = { name: "Grace" };
lead.name = "Grace Patel";   // allowed

// Missing properties are undefined, not an error
lead.phone;                  // undefined
lead.phone?.trim();          // undefined: optional chaining avoids a crash
lead.phone ?? "no phone";    // "no phone": default for null/undefined

// Numbers: one type, floating point
0.1 + 0.2;                   // 0.30000000000000004
```

## Arrays and objects

```javascript
const leads = [
  { name: "Grace Patel", source: "website", hours: 30 },
  { name: "Omar Ali", source: "ad", hours: 2 },
];

const late = leads.filter((l) => l.hours > 24).map((l) => l.name);    // ["Grace Patel"]

const bySource = {};
for (const l of leads) {
  bySource[l.source] = (bySource[l.source] ?? 0) + 1;
}
console.log(bySource);    // { website: 1, ad: 1 }

const { name, source } = leads[0];   // destructuring
const copy = { ...leads[0], hours: 0 };   // spread: copy with a change
```

## Modules

```javascript
// normalize.js
export function normalizeEmail(value) {
  return value.trim().toLowerCase();
}

// main.js
import { normalizeEmail } from "./normalize.js";
```

(For `import` to work in Node, name files `.mjs` or add `"type": "module"` to `package.json`.)

## Promises and async/await

JavaScript is built around non-blocking I/O, so network calls return a **Promise**, a value that will arrive later. Use `async`/`await`, just like Python (Lesson 15):

```javascript
async function getRepo() {
  const response = await fetch("https://api.github.com/repos/python/cpython");
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
  return data.full_name;
}

getRepo()
  .then((name) => console.log(name))
  .catch((err) => console.error("failed:", err.message));
```

Concurrent requests: `await Promise.all([fetch(a), fetch(b)])`, the equivalent of `asyncio.gather`.

## The DOM, briefly

In a browser, JavaScript changes the page through the **DOM** (Document Object Model):

```html
<button id="load">Load leads</button>
<ul id="list"></ul>
<script>
  document.querySelector("#load").addEventListener("click", async () => {
    const leads = await (await fetch("/leads.json")).json();
    const list = document.querySelector("#list");
    list.innerHTML = "";
    for (const lead of leads) {
      const li = document.createElement("li");
      li.textContent = `${lead.name} (${lead.course})`;   // textContent, never innerHTML, for data
      list.appendChild(li);
    }
  });
</script>
```

Use `textContent` for data: putting user-supplied text into `innerHTML` lets attackers inject scripts (cross-site scripting, covered in Module 10). In Module 04, React handles the DOM for you.

## npm

`npm` is JavaScript's package manager, like pip:

```bash
npm init -y
```

```bash
npm install date-fns
```

Dependencies are recorded in `package.json`; installed code goes in `node_modules/` (never commit it).

## Check yourself

Write `stats.mjs` that reads an AdmitFlow JSON export (`leads.json`, created by `admitflow import`) with `import { readFile } from "node:fs/promises"` and prints the number of leads per course, highest first. (Exercise set 05 walks through this.)

Next: [Lesson 19 — TypeScript basics](19-typescript-basics.md)
