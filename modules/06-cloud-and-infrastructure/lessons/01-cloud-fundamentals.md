# Lesson 01 — Cloud fundamentals

**Time:** ~3 hours · **Core**

## Why this matters

"Deploy it" means different things at every client: their AWS account, their Azure tenant, an on-premise server, or a VM in a hospital basement. You need a model of the options that's independent of any one provider, so you can work in whatever the client already has.

## What "the cloud" is

Renting computing resources (servers, storage, databases, networks) from a provider, on demand, paid by use, managed through an API.

## Service models

| Model | You manage | Provider manages | Examples | AdmitFlow piece |
| --- | --- | --- | --- | --- |
| **IaaS** (infrastructure) | OS, runtime, app, data | Hardware, network, virtualization | EC2, Compute Engine, Azure VMs | The office VM |
| **PaaS** (platform) | App, data, config | OS, runtime, scaling, patching | Cloud Run, App Runner, Container Apps, App Service | API container |
| **Managed services** | Data, config | Everything else | Cloud SQL, RDS, Azure Database for PostgreSQL | Database |
| **SaaS** (software) | Your data and settings | The whole application | Google Workspace, Salesforce, HubSpot | Email, CRM |

**FDE default:** use the most managed option the client allows. A part-time IT administrator (Mr. Okafor) can't patch operating systems and tune databases, but he can own a managed database with automatic backups.

## The shared responsibility model

The provider secures **the cloud** (data centres, hardware, their services). You secure **what you put in it**: identities and permissions, network rules, data, secrets, application code. Most cloud breaches are configuration mistakes on the customer side: public storage buckets, leaked keys, over-broad permissions.

## Core building blocks (every provider has them)

| Block | What it is | Names you'll see |
| --- | --- | --- |
| **Region / zone** | Where it physically runs | `asia-south1`, `eu-west-1`, "Central India" |
| **Compute** | Run code | VMs, containers, functions |
| **Storage** | Files and objects | S3, Cloud Storage, Blob Storage |
| **Database** | Managed SQL/NoSQL | RDS, Cloud SQL, Cosmos DB |
| **Network** | Private networks, firewalls, load balancers, DNS | VPC/VNet, security groups, Cloud Load Balancing |
| **Identity (IAM)** | Who/what can do what | IAM roles, service accounts, Entra ID |
| **Secrets** | Store keys and passwords | Secrets Manager, Secret Manager, Key Vault |
| **Observability** | Logs, metrics, alerts | CloudWatch, Cloud Monitoring, Azure Monitor |

The [deployment guide's comparison table](../../../projects/admitflow/deploy/README.md#what-gets-deployed) maps every AdmitFlow piece onto AWS, Google Cloud and Azure.

## Regions and data residency

Choose a region close to users (lower latency) **and** allowed by the client's rules. Many organizations, and some laws, require personal data to stay in a particular country or region. Ask early: "Are there rules about where student data may be stored?"

## Public, private, hybrid

- **Public cloud:** the providers above.
- **Private cloud / on-premise:** the client's own data centre or servers.
- **Hybrid:** both connected, e.g. the student information system stays on the office server while AdmitFlow runs in the cloud and reads a weekly export.

Hybrid is extremely common in FDE work. The integration between the two worlds (VPNs, firewalls, file transfers) is often the hardest part.

## Paying for it

Cloud bills are usage-based and can surprise people. Know the main cost drivers: always-on compute, database size and tier, data transfer out of the cloud, and storage. Lesson 08 covers estimates and budget alerts. **Set a budget alert on day one of any project.**

## Pick one provider, learn it well

The concepts transfer; the console screens don't. Pick the provider your target employers or clients use most, and learn its compute, database, IAM and logging properly. This module's walkthrough uses Google Cloud Run for its simplicity; equivalents for AWS and Azure are listed throughout.

## Check yourself

For AdmitFlow, choose a service model for each piece (API, dashboard, database, scheduled import, secrets) on the provider of your choice. Justify each in one sentence in terms of what Mr. Okafor will have to maintain.

Next: [Lesson 02 — Linux servers and SSH](02-linux-and-ssh.md)
