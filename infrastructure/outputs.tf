output "s3_bucket_name" {
  value = aws_s3_bucket.readmission_bucket.bucket
}

output "ecs_cluster_name" {
  value = var.localstack_enabled ? null : aws_ecs_cluster.api_cluster[0].name
}

output "sns_topic_arn" {
  value = aws_sns_topic.monitoring_alerts.arn
}
