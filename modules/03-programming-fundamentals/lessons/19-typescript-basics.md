# Lesson 19 — TypeScript basics

**Time:** ~3 hours · **Core**

## Why this matters

TypeScript is JavaScript plus type annotations, checked before your code runs. Most professional frontends (including the React dashboard in Module 04) and many Node.js backends use it. It's the JavaScript equivalent of Python's type hints (Lesson 11), but enforced more strictly.

## Setup

```bash
mkdir ts-practice && cd ts-practice
```

```bash
npm init -y
```

```bash
npm install --save-dev typescript tsx
```

- `typescript` provides `tsc`, the type checker and compiler.
- `tsx` runs `.ts` files directly: `npx tsx main.ts`.

Check types without running:

```bash
npx tsc --noEmit --strict main.ts
```

## Types on variables and functions

```typescript
const course: string = "Data Analytics";
let seats: number = 30;
const isOpen: boolean = true;

function priority(hoursWaiting: number): "urgent" | "high" | "normal" {
  if (hoursWaiting > 48) return "urgent";
  if (hoursWaiting > 24) return "high";
  return "normal";
}

priority("30");   // ❌ error: Argument of type 'string' is not assignable to parameter of type 'number'
```

TypeScript **infers** many types, so `const seats = 30` is already a `number`. Annotate function parameters and return values; let inference handle the rest.

## Describing objects: interfaces and types

```typescript
type Source = "website" | "ad" | "phone" | "walk-in" | "whatsapp";   // a union of exact strings

interface Lead {
  leadId: string;
  name: string;
  email?: string;          // optional
  phone: string | null;    // may be null
  sources: Source[];
}

const zoe: Lead = {
  leadId: "ad_900036",
  name: "Zoë García",
  phone: null,
  sources: ["ad"],
};

zoe.sources.push("fax");   // ❌ error: '"fax"' is not assignable to type 'Source'
```

`interface` and `type` are mostly interchangeable for objects; pick one style per project.

## Handling null safely

With `--strict`, TypeScript forces you to handle missing values:

```typescript
function displayPhone(lead: Lead): string {
  return lead.phone.trim();          // ❌ error: 'lead.phone' is possibly 'null'
}

function displayPhoneSafely(lead: Lead): string {
  return lead.phone?.trim() ?? "no phone";   // ✅
}
```

This catches a whole category of "undefined is not a function" bugs before they reach a client's users.

## Typing API responses

Data from `fetch` is `unknown` to TypeScript until you say what it is:

```typescript
async function loadLeads(): Promise<Lead[]> {
  const response = await fetch("/api/leads");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return (await response.json()) as Lead[];
}
```

`as Lead[]` is a *promise to the compiler*, not a check. If the API sends something else, you'll find out at runtime. For data from systems you don't control, validate it, e.g. with the [zod](https://zod.dev/) library (the JavaScript equivalent of Pydantic, which you'll use in Module 04).

## Generics, briefly

```typescript
function first<T>(items: T[]): T | undefined {
  return items[0];
}

const firstLead = first([zoe]);   // type: Lead | undefined
```

`T` is a type parameter, so one function works for any type, safely.

## Check yourself

Convert your `stats.mjs` from Lesson 18 to `stats.ts` with a `Lead` interface. Run it with `npx tsx stats.ts`, then introduce a deliberate typo (`lead.cuorse`) and see what `npx tsc --noEmit --strict stats.ts` reports.

Next: [Exercises](../exercises/README.md) and the [build](../build.md).
