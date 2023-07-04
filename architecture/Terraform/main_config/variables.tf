variable "services" {
  description = "APIs to be enabled."
  type        = list(string)
}

variable "tf_sa" {
  description = "Service account to access GCS backend."
  type        = string
  default     = "tf-iac@<PROJECT_ID>.iam.gserviceaccount.com"
}

variable "project_id" {
  description = "ID of the Google Project"
  type        = string
  default     = "<PROJECT_ID>"
}

variable "region" {
  type        = string
  description = "Default Region"
  default     = "us-central1"
}
