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
