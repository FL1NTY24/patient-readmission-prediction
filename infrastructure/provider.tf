terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
provider "aws" {
  region                      = "us-east-1"
  access_key                  = var.localstack_enabled ? "test" : null
  secret_key                  = var.localstack_enabled ? "test" : null
  skip_credentials_validation = var.localstack_enabled
  skip_requesting_account_id  = var.localstack_enabled
  skip_metadata_api_check     = var.localstack_enabled
  endpoints {
    s3  = var.localstack_enabled ? "http://127.0.0.1:4566" : null
    sns = var.localstack_enabled ? "http://127.0.0.1:4566" : null
  }
}
