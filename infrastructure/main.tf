# S3 bucket for storing dataset and MLflow artifacts
resource "aws_s3_bucket" "readmission_bucket" {
  bucket = var.bucket_name
  tags = {
    Name        = "readmission-bucket"
    Environment = "dev"
  }
}

# S3 bucket ACL to private
resource "aws_s3_bucket_acl" "readmission_bucket_acl" {
  bucket = aws_s3_bucket.readmission_bucket.id
  acl    = "private"
}

# Upload dataset to S3
resource "aws_s3_object" "dataset" {
  bucket = aws_s3_bucket.readmission_bucket.id
  key    = "data/diabetes_data.csv"
  source = "../data/diabetes_data.csv"
  tags = {
    Name = "diabetes-dataset"
  }
}

# ECS cluster for FastAPI deployment
resource "aws_ecs_cluster" "api_cluster" {
  name = var.ecs_cluster_name
  tags = {
    Name        = "readmission-api-cluster"
    Environment = "dev"
  }
}

# SNS topic for monitoring alerts
resource "aws_sns_topic" "monitoring_alerts" {
  name = var.sns_topic_name
  tags = {
    Name        = "readmission-monitoring-alerts"
    Environment = "dev"
  }
}
