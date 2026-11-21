# Lesson 08 — Infrastructure as Code, Kubernetes and cost

**Time:** ~4 hours · **Core** (cost) / *Stretch* (Terraform, Kubernetes)

## Infrastructure as Code (IaC)

Clicking through a console is fine for learning. For a client system it's a problem: nobody can tell exactly what was created, reproduce it in another environment, or review a change before it happens. **IaC** describes infrastructure in files, versioned in Git and applied by a tool.

[Terraform](https://developer.hashicorp.com/terraform) (and its open-source fork OpenTofu) is the most common multi-cloud tool. Each provider also has its own (AWS CloudFormation/CDK, Azure Bicep, Google Cloud Deployment Manager), and Pulumi lets you write IaC in Python or TypeScript.

```hcl
resource "google_sql_database_instance" "db" {
  name             = "admitflow-db"
  database_version = "POSTGRES_16"
  settings {
    tier = "db-f1-micro"
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }
    ip_configuration {
      ipv4_enabled = false                      # no public IP
    }
  }
  deletion_protection = true                    # a bad plan can't delete the client's data
}
```

The workflow:

```bash
terraform init
```

```bash
terraform plan      # shows exactly what would change: review this like a pull request
```

```bash
terraform apply
```

AdmitFlow's teaching example: [`deploy/terraform-cloud-run/main.tf`](../../../projects/admitflow/deploy/terraform-cloud-run/main.tf). Note the least-privilege service account, secrets from Secret Manager, health probes and `deletion_protection`.

Terraform keeps a **state file** recording what it manages. Store it remotely (a locked storage bucket), never in Git: it can contain secrets.

**FDE judgement:** if the client already uses an IaC tool, use theirs. If they use none and have one part-time admin, well-documented console steps (the deployment guide) may be more maintainable for them than Terraform they can't read. Decide with them, and record it in an ADR.

## Kubernetes (awareness)

Kubernetes runs containers across a cluster of machines, with scheduling, self-healing, scaling, service discovery and rolling deployments. It's powerful and widely used at large clients, and it's also a lot to operate.

| You'll hear | Means |
| --- | --- |
| Pod | One or more containers deployed together |
| Deployment | Keeps N pods of a version running; rolls out updates |
| Service | A stable network name for a set of pods |
| Ingress | HTTP(S) routing from outside into services |
| ConfigMap / Secret | Configuration / secrets mounted into pods |
| Helm chart | A packaged, configurable set of Kubernetes manifests |
| Managed Kubernetes | EKS (AWS), GKE (Google), AKS (Azure) |

If a client runs Kubernetes, you'll typically receive a namespace and a deployment process; your container, health checks and configuration-from-environment habits transfer directly. For a client of AdmitFlow's size, Kubernetes would be overkill.

*Stretch:* the [Kubernetes basics tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/); deploy the course-catalogue image to a local cluster with `kind` or `minikube`.

## Cost: estimate, monitor, control

Clients remember surprise bills. Ms. Chen asked in Module 01 for **predictable monthly costs**.

**Estimate before building**, with the provider's pricing calculator, listing each resource:

| Resource | Sizing assumption | Monthly estimate |
| --- | --- | --- |
| API containers | 6 users, scale to zero, ~X requests/day | from calculator |
| Managed PostgreSQL | smallest tier, 10 GB, backups | from calculator (usually the largest item) |
| Storage + CDN for dashboard | < 1 GB, low traffic | |
| Logs | default retention | |
| Data transfer | low | |

(Prices change and vary by region, so this handbook doesn't quote them. Always use the current calculator and note the date.)

**Monitor and control:**
- **Budget alerts** at 50%, 90% and 100% of the agreed monthly amount, emailed to you *and* the client's owner
- **Labels/tags** on every resource (`project=admitflow`, `env=prod`, `owner=…`) so costs can be attributed
- **Caps:** `max_instances`, log retention, storage lifecycle rules
- **Clean up** experiments and old images
- Review the bill monthly for the first three months

Common surprises: an always-on database tier larger than needed, forgotten test resources, verbose logging at scale, and data transfer out of the cloud.

## Check yourself

Do [Exercise 03](../exercises/03-cost-estimate.md): a cost estimate for AdmitFlow on your chosen provider, with assumptions, a monthly total range, a budget-alert plan, and the three biggest risks to the estimate.

Next: [Exercises](../exercises/README.md) and the [build](../build.md).
