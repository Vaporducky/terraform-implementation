resource "google_cloudfunctions_function" "this" {
  depends_on = [google_storage_bucket_object.this]

  name        = var.cf_name
  description = "My function"
  runtime     = "python310"

  source_archive_bucket        = google_storage_bucket.cloud_function_bucket.name
  source_archive_object        = google_storage_bucket_object.this.name
  trigger_http = true
  https_trigger_security_level = "SECURE_ALWAYS"

  environment_variables = {
    PROJECT_ID = var.project_id
    TOPIC_ID = var.topic_id
  }

  service_account_email = google_service_account.this.email
}

# IAM entry for a single user to invoke the function
/* resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "user:myFunctionInvoker@example.com"
} */