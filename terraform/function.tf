data "archive_file" "source" {
    type        = "zip"
    source_dir  = "../src"
    output_path = "/tmp/function.zip"
}

resource "google_storage_bucket_object" "zip" {
    source       = data.archive_file.source.output_path
    content_type = "application/zip"

    name         = "src-${data.archive_file.source.output_md5}.zip"
    bucket       = google_storage_bucket.function_bucket.name
}

resource "google_cloudfunctions_function" "function" {
    name = "function-trigger-on-gcs"
    runtime = "python38"

    source_archive_bucket = google_storage_bucket.function_bucket.name
    source_archive_object = google_storage_bucket_object.zip.name

    entry_point = "hello_gcs"

    event_trigger {
        event_type = "google.storage.object.finalize"
        resource = "${var.project_id}-input"
    }
}

