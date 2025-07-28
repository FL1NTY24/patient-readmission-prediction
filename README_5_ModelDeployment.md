## Model Deployment

Objective
Deploy the trained ReadmissionModel (Random Forest Classifier) as a REST API using FastAPI, containerize it with Docker, and deploy it to AWS ECS (simulated locally via LocalStack for cost-free testing). The deployment will enable real-time inference for patient readmission risk prediction, be accessible for testing, and meet the 4-point model deployment criteria.

Prerequisites
Existing Setup (from Steps 1–6):
mlops_project.py and pipeline.py successfully train and log the ReadmissionModel to MLflow (tracking URI: http://127.0.0.1:5000, SQLite backend: sqlite:///mlflow.db, S3 artifacts: s3://readmission-bucket/mlflow-artifacts).
diabetes_data.csv (UCI Diabetes 130-Hospitals Dataset) is in C:\Users\<rootuserfolder>\patient-readmission-prediction\data.
LocalStack is running with S3, ECR, ECS, and CloudWatch services (ports 4566, 4510-4559).
Terraform scripts in infrastructure/ provision an S3 bucket (readmission-bucket) and SNS topic.
Python 3.9.13, Docker Desktop with WSL2 integration, Terraform 1.9.4, LocalStack, and AWS CLI are installed (per Step 3 README).
AWS credentials are configured for optional AWS deployment.
Tools:
FastAPI and Uvicorn for the REST API.
Docker for containerization.
LocalStack for simulating AWS ECS, ECR, and S3.
MLflow for loading the registered model.
AWS CLI (awslocal) for LocalStack interactions.
Pydantic for input validation.

Step-by-Step Plan
Create FastAPI Application (app.py) Develop a FastAPI application to serve the ReadmissionModel via a /predict endpoint for readmission probability and a /health endpoint for ECS health checks.
app.py
python
Edit in files
•
Show inline
Details:

Endpoint: /predict accepts POST requests with patient data (matching the training schema: age, gender, race, time_in_hospital, num_lab_procedures, num_medications, diabetesMed) and returns the readmission probability.
Health Check: /health supports ECS health checks.
Model Loading: Loads the latest ReadmissionModel from MLflow’s Production stage.
Input Validation: Uses Pydantic to enforce the input schema.
Error Handling: Raises HTTP exceptions for invalid inputs or model loading failures.
Schema Handling: Converts inputs to float64 to match the training data schema, avoiding type mismatches.
Create Dockerfile Define a Docker container to run the FastAPI application.
Dockerfile
dockerfile
Edit in files
•
Show inline
Details:

Base Image: python:3.9-slim ensures compatibility with your Python 3.9.13 environment and keeps the image lightweight.
Dependencies: Installs dependencies from requirements.txt.
Port: Exposes 8000 for FastAPI.
Command: Runs the app with uvicorn for production-grade serving.
Update requirements.txt Update the dependencies file to include FastAPI and Uvicorn, ensuring pinned versions for reproducibility.
requirements.txt
plain
Edit in files
•
Show inline
Details:

Includes dependencies from mlops_project.py and pipeline.py (e.g., pandas, scikit-learn, mlflow, prefect).
Adds fastapi and uvicorn for the API.
Pinned versions ensure reproducibility (Step 9, 4 points).
Create ECS Task Definition (ecs_task_definition.json) Define the ECS task to run the Docker container in LocalStack.
ecs_task_definition.json
json
Edit in files
•
Show inline
Details:

Family: Unique task name (readmission-task).
Container: Uses the readmission-prediction:latest image.
Port: Maps 8000 for API access.
Environment: Sets LocalStack and MLflow variables for model loading.
Health Check: Uses the /health endpoint to verify container health.
Fargate: Simulates serverless deployment with minimal CPU (256) and memory (512 MB) to stay within AWS Free Tier limits.
Create Deployment Script (deploy_ecs.sh) Automate the ECS cluster, service, and task deployment in LocalStack.
deploy_ecs.sh
x-shellscript
Edit in files
•
Show inline
Details:

Builds and pushes the Docker image to LocalStack’s ECR.
Creates an ECR repository, ECS cluster, and service.
Uses dummy subnet and security group IDs (to be replaced with actual IDs from LocalStack).
Handles both creation and updating of the ECS service for robustness.
Includes error handling (set -e) to stop on failures.
Test Locally (Before ECS)
Verify the FastAPI application and Docker container locally to ensure functionality before ECS deployment.

Steps:

Save Files: Save app.py, Dockerfile, requirements.txt, ecs_task_definition.json, and deploy_ecs.sh in C:\Users\<rootuserfolder>\patient-readmission-prediction.
Make deploy_ecs.sh Executable (on Windows, use WSL):

cd C:\Users\<rootuserfolder>\patient-readmission-prediction
wsl
chmod +x deploy_ecs.sh

Verify:
ls -l deploy_ecs.sh

Expected output: -rwxrwxrwx

Exit WSL:

exit

Install Dependencies:

cd C:\Users\<rootuserfolder>\patient-readmission-prediction
py -m pip install fastapi==0.99.1 uvicorn==0.30.6
Verifies: fastapi==0.99.1 uvicorn==0.30.6.
Start LocalStack:

docker run -d -p 4566:4566 -p 4510-4559:4510-4559 --env SERVICES=s3,ecr,ecs,cloudwatch --env HOSTNAME_EXTERNAL=localhost --env S3_PATH_STYLE=1 localstack/localstack
Verifies: LocalStack is running with S3, ECR, ECS, and CloudWatch services.
Start MLflow Server (If not running already):

cd C:\Users\<rootuserfolder>
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 127.0.0.1 --port 5000
Verifies: MLflow UI is accessible at http://127.0.0.1:5000, and ReadmissionModel is in the Production stage.
Test FastAPI Locally:
powershell

Collapse

Wrap

Copy
cd C:\Users\<rootuserfolder>\patient-readmission-prediction
uvicorn app:app --host 0.0.0.0 --port 8000
Open http://127.0.0.1:8000/docs in a browser to view the Swagger UI.
Test the /predict endpoint:

curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Expected Output: {"readmission_probability": <float>} (e.g., {"readmission_probability": 0.73})
Test the /health endpoint:

curl -X GET "http://127.0.0.1:8000/health"
Expected Output: {"status": "healthy"}
Stop Uvicorn with Ctrl+C.
Build and Test Docker Container:

docker build -t readmission-prediction:latest .
docker run -d -p 8000:8000 --env AWS_ENDPOINT_URL=http://host.docker.internal:4566 readmission-prediction:latest
Test the /predict endpoint:

curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Expected Output: {"readmission_probability": <float>}
Test the /health endpoint:

curl -X GET "http://127.0.0.1:8000/health"
Expected Output: {"status": "healthy"}
Stop the container:

docker ps
docker stop <container_id>
Deploy to ECS (LocalStack)
Deploy the Docker container to a simulated AWS ECS environment using LocalStack to meet the cloud deployment criterion.

Steps:

Ensure LocalStack is Running (from Step 6.4).
Create LocalStack Network Resources:

awslocal ec2 create-vpc --cidr-block 10.0.0.0/16
awslocal ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24
awslocal ec2 create-security-group --group-name readmission-sg --description "SG for readmission API" --vpc-id <vpc-id>
awslocal ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 8000 --cidr 0.0.0.0/0
Capture the <vpc-id> and <sg-id> from the output.
Update deploy_ecs.sh with these IDs (replace SUBNET_ID=subnet-12345678 and SECURITY_GROUP_ID=sg-12345678).
Run Deployment Script (use Git Bash or WSL on Windows):

cd C:\Users\<rootuserfolder>\patient-readmission-prediction
./deploy_ecs.sh
Verifies: Docker image is built, pushed to LocalStack ECR, ECS cluster/service/task are created.
Verify ECS Deployment:

awslocal ecs list-services --cluster readmission-cluster
awslocal ecs describe-services --cluster readmission-cluster --services readmission-service
Expected Output: Lists the readmission-service with desiredCount: 1 and runningCount: 1.
Test the API (LocalStack forwards to port 8080):

curl -X POST "http://127.0.0.1:8080/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Expected Output: {"readmission_probability": <float>}
Test the /health endpoint:

curl -X GET "http://127.0.0.1:8080/health"
Expected Output: {"status": "healthy"}
Note on LocalStack ECS Limitation: If ECS deployment fails due to LocalStack’s free tier limitations (as noted in your README), the local Docker container test (Step 6) demonstrates that the code is containerized and cloud-ready, meeting the 4-point criteria. You can proceed to Step 8 for AWS deployment if required for the demo.
Optional AWS Free Tier Deployment
For the final demo, deploy to AWS ECS using the free tier and terminate resources immediately to avoid costs.

Steps:

Update Terraform Scripts (in infrastructure/):
Modify provider.tf to use real AWS credentials:

provider "aws" {
  region     = "<userregion>"
  access_key = "<useraccesskey>"
  secret_key = "<secretkey>"
}
Update variables.tf to set localstack_enabled=false.
Ensure main.tf provisions an ECS cluster, task definition, and service (as per Step 3).
Apply Terraform:

cd C:\Users\<rootuserfolder>\patient-readmission-prediction\infrastructure
terraform init
terraform apply -var="localstack_enabled=false" -auto-approve
Verifies: Provisions S3 bucket, ECS cluster, and SNS topic in AWS.
Update deploy_ecs.sh for AWS:
Replace localhost:4566 with your AWS account’s ECR URI (e.g., <account-id>.dkr.ecr.us-east-1.amazonaws.com).
Example:

IMAGE_NAME=readmission-prediction
TAG=latest
ECR_REPOSITORY=readmission-ecr
ECR_URI=<account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag $IMAGE_NAME:$TAG $ECR_URI/$ECR_REPOSITORY:$TAG
docker push $ECR_URI/$ECR_REPOSITORY:$TAG
Run Deployment Script:

cd C:\Users\<rootuserfolder>\patient-readmission-prediction
./deploy_ecs.sh
Test the API:
Get the ECS service’s public IP or Application Load Balancer (ALB) URL from the AWS Console (ECS > Clusters > readmission-cluster > Services > readmission-service).
Test:

curl -X POST "<ecs-url>:8000/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Expected Output: {"readmission_probability": <float>}
Test the /health endpoint:

curl -X GET "<ecs-url>:8000/health"
Expected Output: {"status": "healthy"}
Terminate Resources (to ensure zero cost):

terraform destroy -var="localstack_enabled=false" -auto-approve
Verifies: All AWS resources (ECS cluster, ECR repository, etc.) are deleted.
