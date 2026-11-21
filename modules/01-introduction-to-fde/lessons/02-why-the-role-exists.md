# Lesson 02 — Why the role exists

**Time:** ~1.5 hours · **Core**

## The last-mile problem

Every powerful technology has a **last-mile problem**: the gap between what the technology *can* do and what it *actually does* inside a specific organization.

A database can store anything, but someone has to design the schema for *this* hospital. An LLM can answer questions, but someone has to connect it to *this* bank's documents, respect *this* bank's permissions, and prove to *this* bank's risk team that it won't leak data.

Products are built to be general. Customers are specific. FDEs close that gap.

## Why the gap is wide in enterprises

Picture a typical company that wants to "use AI":

| Reality inside the company | Why a product alone doesn't fix it |
| --- | --- |
| Data spread across a CRM, an ERP, spreadsheets, email and a 15-year-old internal tool | The product doesn't know where the data is, what it means, or how clean it is |
| Legacy systems with no modern API | Someone has to build the bridge |
| Security, privacy and compliance rules | The solution must pass reviews the vendor has never seen |
| Departments with different workflows | "The process" is really five processes |
| Unclear success criteria | Nobody has defined what "working" means |
| Staff who are busy and sceptical | If it doesn't fit their day, they won't use it |

Each of these is solvable, but only by someone who is close enough to see the details and technical enough to act on them.

## Why traditional approaches fall short

| Approach | Where it struggles |
| --- | --- |
| **Sell the product, customer implements it** | Customer lacks the skills or time; the project stalls after purchase |
| **Hand off to a systems integrator** | Long timelines, high cost, knowledge lost between parties |
| **Product team builds custom features** | Slow, distracts from the core product, built far from the problem |
| **Customer's own IT builds it** | Often lacks experience with the new technology |

The FDE model puts an engineer from the company that deeply understands the technology *directly* into the customer's problem, with the authority to build.

## Prototype vs. production: the AI version of the gap

AI made this gap far more visible. A demo of an AI assistant can be built in an afternoon. Getting it to production often takes months, because production requires:

- **Real data**, which is messier than demo data
- **Accuracy that's measured**, not "it looked right in the demo"
- **Permissions**, so the assistant can't show an intern the CEO's salary
- **Integration**, so it works inside the tools people already use
- **Monitoring**, so you know when it starts getting things wrong
- **Trust**, so people actually use it

Most failed AI projects don't fail because the model was too weak. They fail at one of these steps. FDEs specialize in getting through them.

## What the business gets

When the model works, the customer gets measurable outcomes faster. The company providing the FDEs gets:

- **Adoption and retention:** customers who see value keep paying
- **Product insight:** FDEs see real problems first-hand
- **Reusable assets:** solutions built for one customer become templates or features for others

The trade-off is cost: FDEs are expensive, and embedding engineers doesn't scale like software does. Good FDE organizations manage this by turning repeated custom work into product over time.

## Check yourself

Pick an organization you know (a school, a shop, a hospital, your workplace). List three last-mile problems it would face if it bought a new AI tool tomorrow.

Next: [Lesson 03 — FDE vs. neighbouring roles](03-fde-vs-other-roles.md)
