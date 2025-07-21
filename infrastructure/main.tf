resource "aws_s3_bucket" "readmission_bucket" {
  bucket = var.bucket_name
  tags = {
    Name        = var.bucket_name
    Environment = "dev"
  }
}

resource "aws_s3_bucket_acl" "readmission_bucket_acl" {
  bucket = aws_s3_bucket.readmission_bucket.id
  acl    = "private"
}

resource "aws_s3_object" "dataset" {
  bucket = aws_s3_bucket.readmission_bucket.id
  key    = "data/diabetes_data.csv"
  source = "../data/diabetes_data.csv"
  tags = {
    Name = "diabetes-dataset"
  }
}

resource "aws_sns_topic" "monitoring_alerts" {
  name = var.sns_topic_name
  tags = {
    Name        = var.sns_topic_name
    Environment = "dev"
  }
}

resource "aws_ecs_cluster" "api_cluster" {
  count = var.localstack_enabled ? 0 : 1  # Skip ECS in LocalStack
  name  = var.ecs_cluster_name
  tags = {
    Name        = var.ecs_cluster_name
    Environment = "dev"
  }
}
