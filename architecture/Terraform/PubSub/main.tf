resource "google_pubsub_schema" "bicycle_analytics_schema" {
  name       = "bicycle_analytics_${var.topic_id}_schema"
  type       = "AVRO"
  definition = var.schema_definition
}

resource "google_pubsub_topic" "bicycle_analytics_report" {
  name       = var.topic_id
  depends_on = [google_pubsub_schema.example]
  schema_settings {
    schema   = "projects/${var.project_id}/schemas/${google_pubsub_schema.bicycle_analytics_schema.name}"
    encoding = "JSON"
  }
}

resource "google_pubsub_subscription" "bicycle_analytics_dataflow" {
  name  = var.subscription_id
  topic = google_pubsub_topic.bicycle_analytics_parameters.name

  ack_deadline_seconds            = 60
  enable_menable_message_ordering = true
  message_retention_duration      = "10h"

  expiration_policy {
    # Never expires
    ttl = ""
  }

}
