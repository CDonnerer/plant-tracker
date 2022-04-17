resource "google_cloud_scheduler_job" "hello-world-job" {
    name = "watering-report-scheduler"
    description = "Set schedule for producing watering report"
    schedule = "0 9 * * 6"

    http_target {
        http_method = "GET"
        uri = google_cloudfunctions_function.function.https_trigger_url
        oidc_token {
            service_account_email = var.service_account
        }
    }
}