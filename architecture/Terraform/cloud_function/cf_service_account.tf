resource "google_service_account" "this" {
  project = var.project_id

  account_id   = var.sa_name
  display_name = "[Bicycle Report] Parameter Publisher"
  description = "Service account to publish to PubSub topic \"${var.topic_id}\""
}

resource "google_project_iam_member" "this" {
  depends_on = [google_service_account.this]

  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.this.email}"
}