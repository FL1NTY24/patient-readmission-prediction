variable "localstack_enabled" {
  type    = bool
  default = false
}

variable "bucket_name" {
  type    = string
  default = "readmission-bucket"
}

variable "ecs_cluster_name" {
  type    = string
  default = "readmission-api-cluster"
}

variable "sns_topic_name" {
  type    = string
  default = "readmission-monitoring-alerts"
}
