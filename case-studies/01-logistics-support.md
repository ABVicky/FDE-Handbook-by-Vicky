# Case 01 — The chatbot nobody needed

🧪 **Illustrative composite.** Not about a real company.
**Industry:** Logistics · **Lifecycle focus:** Discover, Define

## Situation
A regional parcel-delivery company receives ~4,000 customer contacts a day. Support costs are rising and wait times on the phone line exceed 20 minutes. The COO asks the AI vendor's FDE for "a chatbot to replace half the support team."

*Stop here. What would you do first?*

## What discovery found
The FDE spent two days with support agents and pulled a sample of 1,000 tickets:
- **~62%** were "Where is my parcel?"
- Agents answered these by looking up tracking in a legacy desktop application, a 2–3 minute task, mostly waiting for the app.
- The tracking data *already existed*; customers just couldn't see it, because the website's tracking page was broken for parcels handed to partner couriers.
- Of the remaining contacts, many were complex (damage claims, address changes) and needed humans.

## What was built
1. A small service that read tracking events from the legacy system's nightly database export and partner couriers' APIs, combining them into one status.
2. A fixed public tracking page plus proactive SMS updates on delays.
3. Only *then*, a narrow assistant answering "where is my parcel" in chat using the same service, handing everything else to agents with the context pre-filled.

## What went wrong
- The nightly export meant tracking was up to 24 hours stale. The FDE had to negotiate read access to the live database with a cautious IT team, which took three weeks.
- One partner courier's API returned inconsistent status codes; a mapping table had to be maintained by hand.

## Outcome (illustrative)
"Where is my parcel" contacts fell substantially within two months, and phone wait times dropped. Most of the gain came from fixing tracking visibility, not from the chatbot.

## Lessons
- The requested solution (chatbot) was a guess at the problem (customers can't see tracking).
- Fixing the data and the existing channel delivered most of the value.
- Data access negotiation was the critical path, not model choice.

## Discussion questions
1. How would you explain to the COO that the chatbot isn't the main fix, without losing their support?
2. What success metrics would you agree on before starting?
3. What could go wrong if the team had launched the chatbot on top of stale tracking data?
