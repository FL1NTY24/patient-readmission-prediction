# Summary of executed PowerShell Commands for Cloud Setup

# 1. Installed and Configured WSL2 (for Docker)

Installed WSL2 and Virtual Machine Platform:

wsl --install

wsl --set-default-version 2

Installed Ubuntu:

wsl --install -d Ubuntu

Updated WSL:

wsl --update

Verified:

wsl --version

wsl -l -v

# 2. Installed Docker Desktop

Downloaded from docker.com and installed manually.
Configured WSL2 integration in Docker Desktop Settings > Resources > WSL Integration.

Verified:

docker --version

docker run hello-world

docker-compose --version

# 3. Installed Terraform
Downloaded from terraform.io/downloads (e.g., terraform_1.9.4_windows_amd64.zip).
Unzipped and moved terraform.exe to C:\Program Files\Terraform.

Added to PATH (manual via System > Environment Variables > Path)

Verified:

terraform -version

# 4. Installed LocalStack

Verified Python and pip:

python --version

pip --version

Installed LocalStack:

pip install localstack --user

Added Python Scripts to PATH (e.g., C:\Users\GabrielF\AppData\Roaming\Python\Python313\Scripts):

Verified:

localstack --version

Tested with Docker running:

localstack start -d

localstack stop

# 5. Installed and Configured AWS CLI

Installed (download from aws.amazon.com/cli, run .msi)

Verified:
aws --version

Configured:

aws configure

Entered: Required information (Access keys + region etc)

Tested (after adding S3 permissions to IAM user GabrielFlint24):

aws s3 ls

# 6. Created Terraform Scripts

main.tf:

resource "aws_s3_bucket" "readmission_bucket" {
  bucket = var.bucket_name
  tags = {
    Name        = "readmission-bucket"
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
resource "aws_ecs_cluster" "api_cluster" {
  name = var.ecs_cluster_name
  tags = {
    Name        = "readmission-api-cluster"
    Environment = "dev"
  }
}
resource "aws_sns_topic" "monitoring_alerts" {
  name = var.sns_topic_name
  tags = {
    Name        = "readmission-monitoring-alerts"
    Environment = "dev"
  }
}

outputs.tf:

output "s3_bucket_name" {
  value = aws_s3_bucket.readmission_bucket.bucket
}
output "ecs_cluster_name" {
  value = aws_ecs_cluster.api_cluster.name
}
output "sns_topic_arn" {
  value = aws_sns_topic.monitoring_alerts.arn
}

provider.tf:

provider "aws" {
       region = "us-east-1"
       endpoints {
         s3 = var.localstack_enabled ? "http://localhost:4566" : null
       }
       skip_credentials_validation = var.localstack_enabled
       skip_requesting_account_id  = var.localstack_enabled
       skip_metadata_api_check     = var.localstack_enabled
     }
     variable "localstack_enabled" {
       description = "Whether to use LocalStack for local testing"
       type        = bool
       default     = true
     }

variables.tf:

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
