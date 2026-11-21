# Minimal Terraform for AdmitFlow on Google Cloud Run + Cloud SQL (Module 06, stretch).
# ⚠️ Teaching example: review before use; not applied by the handbook authors.
# Usage: terraform init && terraform plan -var project=my-project -var image=REGION-docker.pkg.dev/...

terraform {
  required_version = ">= 1.6"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}

variable "project" { type = string }
variable "region" {
  type    = string
  default = "asia-south1"   # Mumbai; keep data close to users and inside the required jurisdiction
}
variable "image" { type = string }   # the API image pushed to Artifact Registry

provider "google" {
  project = var.project
  region  = var.region
}

resource "google_sql_database_instance" "db" {
  name             = "admitflow-db"
  database_version = "POSTGRES_16"
  settings {
    tier = "db-f1-micro"          # smallest; fine for a pilot, check pricing and limits
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }
    ip_configuration {
      ipv4_enabled = false        # no public IP; Cloud Run connects via the Cloud SQL connector
    }
  }
  deletion_protection = true      # a typo in a plan must not delete the client's data
}

resource "google_sql_database" "admitflow" {
  name     = "admitflow"
  instance = google_sql_database_instance.db.name
}

resource "google_service_account" "api" {
  account_id   = "admitflow-api"
  display_name = "AdmitFlow API (least privilege)"
}

resource "google_project_iam_member" "api_sql_client" {
  project = var.project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_secret_manager_secret" "secret_key" {
  secret_id = "admitflow-secret-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "api_reads_secret" {
  secret_id = google_secret_manager_secret.secret_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}

resource "google_cloud_run_v2_service" "api" {
  name     = "admitflow-api"
  location = var.region
  template {
    service_account = google_service_account.api.email
    scaling {
      min_instance_count = 0     # scale to zero when idle: lowest cost, slower first request
      max_instance_count = 3
    }
    volumes {
      name = "cloudsql"
      cloud_sql_instance { instances = [google_sql_database_instance.db.connection_name] }
    }
    containers {
      image = var.image
      env {
        name = "ADMITFLOW_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.secret_key.secret_id
            version = "latest"
          }
        }
      }
      # DATABASE_URL (with the Cloud SQL socket path and password from Secret Manager) is added the same way.
      startup_probe {
        http_get { path = "/ready" }
      }
      liveness_probe {
        http_get { path = "/health" }
      }
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }
  }
}

output "api_url" { value = google_cloud_run_v2_service.api.uri }
