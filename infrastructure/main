# Defining the S3 bucket for storing dataset and MLflow artifacts
     resource "aws_s3_bucket" "readmission_bucket" {
       bucket = var.bucket_name
       tags = {
         Name        = "readmission-bucket"
         Environment = "dev"
       }
     }

     # Setting S3 bucket ACL to private
     resource "aws_s3_bucket_acl" "readmission_bucket_acl" {
       bucket = aws_s3_bucket.readmission_bucket.id
       acl    = "private"
     }

     # Uploading the dataset to the S3 bucket
     resource "aws_s3_object" "dataset" {
       bucket = aws_s3_bucket.readmission_bucket.id
       key    = "data/diabetes_data.csv"
       source = "../data/diabetes_data.csv"
       tags = {
         Name = "diabetes-dataset"
       }
     }
