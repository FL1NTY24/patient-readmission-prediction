## Cloud Setup

This section outlines the cloud infrastructure setup for the project. The infrastructure is provisioned using **Terraform** (Infrastructure as Code) and supports:
- **S3**: Stores the dataset (`diabetes_data.csv`) and MLflow artifacts.
- **ECS**: Hosts the FastAPI service for model deployment (completed in the **Model Deployment** step).
- **SNS**: Sends monitoring alerts for data drift or model performance issues.
- **LocalStack**: Simulates AWS services locally for cost-free development and testing.
- **AWS Free Tier**: Used for a final demo, with resources terminated to ensure zero cost.

**Terraform** scripts in the `infrastructure/` directory provision all resources. **LocalStack** is used for local testing, and the **AWS Free Tier** is used for a short demo deployment.

### Prerequisites
- **Python**: 3.9 (verified with `python --version`).
- **Docker Desktop**: Configured with WSL2 integration (verified with `docker --version`).
- **Terraform**: ~1.9.4 (verified with `terraform -version`).
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
   
2. **Install Docker Desktop**:
   
Download from docker.com and install.

Enable WSL2 integration in Docker Desktop Settings > Resources > WSL Integration.

Verify:
   ```powershell
   docker --version
   docker run hello-world
   docker-compose --version

3.  **Install Terraform:**:

Download terraform_1.9.4_windows_amd64.zip from terraform.io.

Unzip and move terraform.exe to C:\Program Files\Terraform.

Add C:\Program Files\Terraform to System PATH.

Verify:
```powershell
terraform -version

Install LocalStack:

Verify Python and pip:
```powershell
python --version
pip --version

Install:
```powershell
pip install localstack --user

Add Python Scripts to PATH (e.g., C:\Users\GabrielF\AppData\Roaming\Python\Python313\Scripts).

Verify:
```powershell
localstack --version

Install and Configure AWS CLI:

Download from aws.amazon.com/cli and install via .msi.

Verify:
```powershell
aws --version

Configure with IAM user credentials with AmazonS3FullAccess, AmazonECS_FullAccess, and AmazonSNSFullAccess:
```powershell
aws configure

Enter Access Key ID, Secret Access Key, region (us-east-1), and output format (json).

Test:
```powershell
aws s3 ls

Set Up Terraform Scripts:

Scripts are located in infrastructure/:

main.tf: Provisions S3 bucket, ECS cluster, and SNS topic.

variables.tf: Defines variables (e.g., bucket_name, ecs_cluster_name, sns_topic_name).

outputs.tf: Outputs resource names/ARNs.

provider.tf: Configures AWS provider with LocalStack toggle.

Ensure data/diabetes_data.csv exists in the data/ directory.

Test with LocalStack:

Start LocalStack:
```powershell
localstack start -d

Navigate to infrastructure/:
```powershell
cd patient-readmission-prediction/infrastructure

Initialize Terraform:
```powershell
terraform init

Apply Terraform:
```powershell
terraform apply -var="localstack_enabled=true" -auto-approve

Verify resources:
```powershell
awslocal s3 ls s3://readmission-bucket/
awslocal ecs list-clusters
awslocal sns list-topics

Deploy to AWS Free Tier:

Ensure AWS CLI is configured:
```powershell
aws configure

Apply Terraform for AWS:
```powershell
terraform init
terraform apply -var="localstack_enabled=false" -auto-approve

Verify resources:
```powershell
aws s3 ls s3://readmission-bucket/
aws ecs list-clusters
aws sns list-topics

Terminate resources to avoid charges:
```powershell
terraform destroy -var="localstack_enabled=false" -auto-approve
