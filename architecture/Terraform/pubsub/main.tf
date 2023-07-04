resource "google_pubsub_schema" "bicycle_analytics_schema" {
  name       = "bicycle_analytics_${var.topic_id}_schema"
  type       = "AVRO"
  definition = file(var.schema_definition_file)
}

resource "google_pubsub_topic" "bicycle_analytics_report" {
  name       = var.topic_id
  depends_on = [google_pubsub_schema.bicycle_analytics_schema]
  schema_settings {
    schema   = "projects/${var.project_id}/schemas/${google_pubsub_schema.bicycle_analytics_schema.name}"
    encoding = "JSON"
  }
}

resource "google_pubsub_subscription" "bicycle_analytics_dataflow" {
  name  = var.subscription_id
  topic = google_pubsub_topic.bicycle_analytics_report.name

  ack_deadline_seconds       = 60
  enable_message_ordering    = true
  message_retention_duration = "36000s"

  expiration_policy {
    # Never expires
    ttl = ""
  }

}
