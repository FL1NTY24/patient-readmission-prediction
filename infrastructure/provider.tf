provider "aws" {
  region                      = "us-east-1"
  access_key                  = var.localstack_enabled ? "test" : null
  secret_key                  = var.localstack_enabled ? "test" : null
  skip_credentials_validation = var.localstack_enabled
  skip_requesting_account_id  = var.localstack_enabled
  skip_metadata_api_check     = var.localstack_enabled
  s3_force_path_style         = var.localstack_enabled ? true : false
  endpoints {
    s3  = var.localstack_enabled ? "http://localhost:4566" : null
    sns = var.localstack_enabled ? "http://localhost:4566" : null
  }
}
