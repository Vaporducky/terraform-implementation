resource "google_storage_bucket" "cloud_function_bucket" {
  name     = "var.cf_bucket_name"
  location = "var.region"
  public_access_prevention = "enforced"
}

resource "google_storage_bucket_object" "this" {
  depends_on = [google_storage_bucket.cloud_function_bucket]

  name   = "${var.cf_name}.zip"
  bucket = google_storage_bucket.cloud_function_bucket.name
  source = var.cf_zip_path
}
