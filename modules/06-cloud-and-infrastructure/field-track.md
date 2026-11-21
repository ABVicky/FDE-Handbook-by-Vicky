# Module 06 — Field Track: Deploying into a restricted client environment

**Time:** ~2 hours · **Capabilities:** C4, C5

## Why

Real clients rarely say "here's an empty cloud account, do what you like." They say: *"It has to run in our account, in our region, through our network, using our approved images, and it must pass our security review."* FDEs who plan for that from the start get to go-live; those who don't get stuck in review for weeks.

## The scenario

A second, larger client, a university hospital's nursing school, wants AdmitFlow. Their IT policy says:

- Everything runs in **their** cloud account (Azure), in their approved region only
- No public IP addresses on databases or VMs; inbound traffic only via their existing application gateway
- Container images must come from their private registry, built from approved base images, and pass a vulnerability scan
- External engineers get access only through their VPN, with accounts that expire after 90 days, and no admin rights
- Every new system needs a **security review** (architecture, data flows, data classification, access model) before go-live, and changes go through a weekly change-approval board

## The task

Write `my-work/field-track/m06-deployment-plan.md`:

1. **Architecture** adapted to their rules (a Mermaid diagram), mapping each AdmitFlow piece to an Azure service
2. **Access plan:** what access you need, for how long, and what you can do *without* admin rights (and what you'll need *them* to do)
3. **Security review pack:** list the documents and diagrams you'll prepare, and draft the one-paragraph data-flow description
4. **Timeline** working backwards from a go-live date, including review and change-board lead times
5. **Risks** (at least four) with mitigations, e.g. the review raises an issue, the base image fails the scan, the VPN account expires mid-project
6. **First email** to their IT lead (≤ 200 words): introduce yourself, share the plan, and ask for the three things you need first

## Done when

- [ ] Every policy rule is addressed explicitly in the architecture or access plan
- [ ] The timeline includes the security review and change board
- [ ] The email has a clear, small first ask
