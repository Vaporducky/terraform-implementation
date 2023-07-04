variable "project_id" {
  description = "ID of the Google Project"
  type        = string
  default     = "<PROJECT_ID>"
}

variable "topic_id" {
  description = "Topic ID of the ETL-Composer pipeline"
  default     = "bicycle_analytics_report_parameters"
}

variable "subscription_id" {
  description = "Subscription ID of the ETL-Composer pipeline."
  default     = "bicycle-analytics-dataflow-trigger"
}

variable "schema_definition" {
  description       = "AVRO schema for the topic ID. Ensures consistency."
  schema_definition = file("../../PubSub/Schema/bicycle_analytics_report_parameters_schema.json")
}