terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.30.0"
    }
  }
}

provider "google" {
  project     = var.project
  region      = var.region
}

resource "google_storage_bucket" "data_lake" {
  name                        = var.gcs_bucket_name // must be globally unique
  location                    = var.location
  storage_class               = var.gcs_storage_class
  force_destroy               = true
  uniform_bucket_level_access = true // Enforce uniform bucket-level access


  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload" // Abort multipart uploads that are older than 1 day
    }
  }
}

// Create a BigQuery dataset, format: resource type, resource name
resource "google_bigquery_dataset" "flights_warehouse" {
  dataset_id = var.bq_dataset_name // must be unique within the project
  location   = var.location
}