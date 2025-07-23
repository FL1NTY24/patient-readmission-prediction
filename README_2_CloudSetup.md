## Cloud Setup

This section outlines the cloud infrastructure setup for the project. The infrastructure is provisioned using **Terraform** (Infrastructure as Code) and supports:
- **S3**: Stores the dataset (`diabetes_data.csv`) and MLflow artifacts.
- **ECS**: Hosts the FastAPI service for model deployment (completed in the **Model Deployment** step).
- **SNS**: Sends monitoring alerts for data drift or model performance issues.
- **LocalStack**: Simulates AWS services locally for cost-free development and testing.
- **AWS Free Tier**: Used for a final demo, with resources terminated to ensure zero cost.

**Terraform** scripts in the `infrastructure/` directory provision all resources. **LocalStack** is used for local testing, and the **AWS Free Tier** is used for a short demo deployment.

Note: ECS is not supported in LocalStack’s free tier. When `localstack_enabled=true`, the ECS cluster is skipped (`ecs_cluster_name = null`). Use `localstack_enabled=false` with real AWS credentials for ECS deployment, which may incur costs.

### Prerequisites
- **Python**: 3.9.13 (verified with `python --version`).
- **Docker Desktop**: Configured with WSL2 integration (verified with `docker --version`).
- **Terraform**: 1.12.2 (verified with `terraform -version`). Optionally, upgrade to ~1.9.x for improved stability (download from https://www.terraform.io/downloads.html).
- **LocalStack**: Installed via `pip install localstack --user` (verified with `localstack --version`).
- **AWS CLI**: Installed and configured with IAM user permissions for S3, ECS, and SNS (verified with `aws --version`).
- **WSL2**: Installed on Windows for Docker support (verified with `wsl --version`).
- **GitHub Repository**: Initialized with the project structure.

### Setup Instructions
1. **Install WSL2 (Windows)**:
   ```powershell
   wsl --install
   wsl --set-default-version 2
   wsl --install -d Ubuntu
   wsl --update
   wsl --version
   wsl -l -v
   ```
   
2. **Install Docker Desktop**:
   
- Download from docker.com and install.

- Enable WSL2 integration in Docker Desktop Settings > Resources > WSL Integration.

- Verify:
   ```powershell
   docker --version
   docker run hello-world
   docker-compose --version
   ```

3. **Install Terraform**:
- Download terraform_1.9.4_windows_amd64.zip from terraform.io.

- Unzip and move terraform.exe to C:\Program Files\Terraform.

- Add C:\Program Files\Terraform to System PATH.

- Verify:
   ```powershell
   terraform -version
   ```

4. **Install LocalStack**:

- Verify Python and pip:
   ```powershell
   python --version
   pip --version
   ```

- Install LocalStack and AWS CLI Local:
   ```powershell
   py -m pip install localstack awscli
   ```

- Add Python Scripts to PATH (e.g., C:\Users\GabrielF\AppData\Local\Programs\Python\Python39\Scripts).
  
- Verify installations:
   ```powershell
   localstack --version
   awslocal --version
   ```

5. **Install and Configure AWS CLI**:

- Download from aws.amazon.com/cli and install via .msi.

- Verify:
   ```powershell
   aws --version
   ```

- Configure with IAM user credentials with AmazonS3FullAccess, AmazonECS_FullAccess, and AmazonSNSFullAccess:
   ```powershell
   aws configure
   ```

- Enter Access Key ID, Secret Access Key, region (us-east-1), and output format (json).

- Start LocalStack for test:
   ```powershell
   localstack start -d
   ```
   
- Test (ensure LocalStack is running and AWS_ENDPOINT_URL is set):
   ```powershell
   $env:AWS_ENDPOINT_URL = "http://127.0.0.1:4566"
   awslocal s3 ls
   ```

6. **Set Up Terraform Scripts**:

- Scripts are located in infrastructure/:

   main.tf: Provisions S3 bucket, ECS cluster, and SNS topic.

   variables.tf: Defines variables (e.g., bucket_name, ecs_cluster_name, sns_topic_name).

   outputs.tf: Outputs resource names/ARNs.

   provider.tf: Configures AWS provider with LocalStack toggle.

- Ensure data/diabetes_data.csv exists in the data/ directory.
    ```powershell
   dir data\diabetes_data.csv
    ```

7. **Test with LocalStack**:

- Start LocalStack:
   ```powershell
   localstack start -d
   ```

- Navigate to infrastructure:
   ```powershell
   cd patient-readmission-prediction/infrastructure
   ```



- Initialize Terraform:
   ```powershell
   terraform init
   ```

- Restart LocalStack with Explicit Configuration:
  Stop any existing LocalStack container and start a new one with S3 and SNS services, ensuring path-style addressing for S3 compatibility.
   ```powershell
  docker ps
  docker stop <localstack_container_id>
  docker run -d -p 4566:4566 -p 4510-4559:4510-4559 --env SERVICES=s3,sns --env HOSTNAME_EXTERNAL=localhost --env S3_PATH_STYLE=1 localstack/localstack
  ```

- Test Connectivity:
  ```powershell
  curl http://127.0.0.1:4566
  ```

- Set Environment Variable:
  ```powershell
  $env:AWS_S3_FORCE_PATH_STYLE = "true"
  $env:AWS_ENDPOINT_URL = "http://127.0.0.1:4566"
  ```

- Test LocalStack S3 and SNS Services:
Before running Terraform, verify that LocalStack’s S3 and SNS services are operational:
  ```powershell
  awslocal s3 mb s3://test-bucket
  awslocal s3 ls
  awslocal sns create-topic --name test-topic
  awslocal sns list-topics
  ```

- Apply Terraform:
   ```powershell
  terraform apply -var="localstack_enabled=true" -auto-approve
   ```

- Verify resources:
   ```powershell
   awslocal s3 ls s3://readmission-bucket/
   awslocal sns list-topics
   terraform output
   ```
   
- Terminate LocalStack resources to clean up the local environment (**Only terminate at the end of project**):
   ```powershell
   terraform destroy -var="localstack_enabled=true" -auto-approve
   ```
