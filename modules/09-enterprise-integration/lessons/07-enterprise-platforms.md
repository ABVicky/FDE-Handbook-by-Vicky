# Lesson 07 — Enterprise platforms: CRM, ERP, ITSM and data platforms

**Time:** ~3 hours · **Core** (awareness) / *Stretch* (hands-on with a developer account)

You won't master these platforms in a module. The goal is to recognize them, know how they're usually integrated, and know what to ask for on day one.

## What to ask for, whatever the platform

1. A **sandbox / developer environment**, never production for development
2. An **integration user or service account** with the minimum permissions, plus who approves it
3. The **API limits** for the client's licence (calls per day, bulk limits)
4. Their **custom objects and fields** (every enterprise customizes heavily)
5. The **admin contact** for the platform, and their change process

## The platforms

| Platform | What it is | Integration surfaces | FDE notes |
| --- | --- | --- | --- |
| **Salesforce** | CRM and much more; huge ecosystem | REST & SOAP APIs, Bulk API, Streaming/Platform Events, Apex code, Flows | Strict per-org API limits; objects heavily customized; Connected Apps for OAuth |
| **HubSpot** | Marketing/sales CRM, common in mid-size orgs | REST APIs (contacts, deals…), webhooks, private-app tokens | Search API is eventually consistent; custom properties needed for your fields |
| **Microsoft Dynamics 365 / Power Platform** | CRM/ERP plus low-code (Power Apps, Power Automate) on Dataverse | Dataverse Web API (OData), Power Automate connectors, Entra ID auth | Expect Entra ID everywhere; clients often want your API exposed as a connector |
| **SAP** | ERP: finance, procurement, HR, supply chain | OData/REST via SAP BTP, BAPIs/RFCs, IDocs, SAP Integration Suite | Slow-moving and change-controlled; always integrate through the client's SAP team |
| **ServiceNow** | IT service management and workflows | REST Table API, Scripted REST, IntegrationHub, webhooks | Great place to raise tickets and approvals from AI workflows |
| **Palantir Foundry / AIP** | Data integration and operational platform with an ontology; AIP adds LLM capabilities | Platform SDKs, ontology actions, pipelines | Often the client's system of record for integrated data; FDE work happens *inside* it |
| **Snowflake / Databricks / BigQuery** | Data warehouses and lakehouses | SQL, connectors, platform-native apps and ML | Read from curated tables; respect the data team's governance |

## Low-code clients

Many organizations build workflows themselves in Power Automate, Zapier or Salesforce Flow. A clean, documented REST API with an OpenAPI spec (FastAPI generates `/openapi.json`) lets them connect your system without you. That's a strong handover asset.

## Working inside a platform vs. alongside it

- **Alongside:** your own service (like AdmitFlow) integrates with the platform via its API. More freedom; more to operate.
- **Inside:** you build within the platform (Salesforce Apex/Flows, Power Apps, Foundry). Less infrastructure, more vendor coupling, and the client's admins can maintain it.

Choose with the client's team. Who will maintain this in two years is usually the deciding question.

## Check yourself

Create a free developer account on one platform (HubSpot developer test account, Salesforce Developer Edition, or a ServiceNow Personal Developer Instance). Create one custom field, then create and update a record through its API with a script. Note: auth method, rate limits, how errors look, and how long setup took.

Next: [Lesson 08 — Model Context Protocol: giving AI safe access to systems](08-mcp.md)
