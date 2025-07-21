variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  default     = "readmission-bucket"
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "readmission-api-cluster"
}

variable "sns_topic_name" {
  description = "Name of the SNS topic"
  type        = string
  default     = "readmission-monitoring-alerts"
}
