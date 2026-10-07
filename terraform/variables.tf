
variable "region" {
  description = "Project Region"
  type        = string
  default     = "europe-west2"

}



variable "project" {
  description = "GCP Project ID"
  type        = string
  default     = "flights-pipeline-510915"
}


variable "location" {
  description = "Project Location"
  type        = string
  default     = "europe-west2"
}



variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  type        = string
  default     = "flights_warehouse"
}


variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  type        = string
  default     = "STANDARD"

}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  type        = string
  default     = "flights-pipeline-data-lake-ya"
}