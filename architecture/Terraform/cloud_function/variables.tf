variable "project_id" {
  description = "ID of the Google Project."
  type        = string
  default     = "<PROJECT_ID>"
}

variable "topic_id" {
  description = "Topic ID of the ETL-Composer pipeline"
  default     = "bicycle_analytics_report_parameters"
}

variable "cf_bucket_name" {
  description = "Name of the bucket which contains the Cloud Function source code."
  default = "publish_parameters_cf_src"
}

variable "cf_bucket_region" {
  description = "Location of the bucket which contains the Cloud Function source code."
  default = "us-central1"
}

variable "cf_name" {
  description = "Name of the Cloud Function."
  default = "publish_parameters"
}

variable "cf_zip_path" {
  description = "Relative path to the Cloud Function zip file."
  default = "../../CloudFunction/publish_parameters.zip"
}

variable "sa_name" {
  description = "Service account which publishes the message to PubSub topic through Cloud Function."
  default = "cf-publish-parameters-bicycle"
}