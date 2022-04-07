variable "project_id" {
    type    = string
    default = "plant-tracker-sandbox"
}

variable "region" {
    default = "europe-west2"
}

variable "service_account" {
    type    = string
    default = "gsheets-connect@plant-tracker-sandbox.iam.gserviceaccount.com"
}
