## Model Deployment

Objective: Deploy the trained ReadmissionModel (Random Forest Classifier) as a REST API using FastAPI, containerize it with Docker, and deploy it to AWS ECS (simulated locally via LocalStack). The deployment should enable real-time inference for patient readmission risk prediction and be accessible for testing.

1. Create FastAPI Application (app.py)
Create a FastAPI application to serve the ReadmissionModel via a /predict endpoint. The endpoint will accept patient data matching the model’s input schema (age, gender, race, time_in_hospital, num_lab_procedures, num_medications, diabetesMed) and return the readmission probability.

app.py
python
Edit in files
•
Show inline
Details:

Endpoint: /predict accepts a POST request with patient data and returns the probability of readmission within 30 days.
Health Check: /health endpoint for ECS health checks.
Model Loading: Loads the latest ReadmissionModel from MLflow.
Input Validation: Uses Pydantic to enforce the input schema.
Schema Handling: Converts inputs to float64 to match the training schema, avoiding integer column issues.
2. Create Dockerfile
Define a Docker container to run the FastAPI application.

Dockerfile
dockerfile
Edit in files
•
Show inline
Details:

Base Image: python:3.9-slim for compatibility with your Python 3.9 environment.
Dependencies: Installs from requirements.txt.
Port: Exposes 8000 for FastAPI.
Command: Runs the app with uvicorn.
3. Update requirements.txt
Add FastAPI and Uvicorn dependencies.

requirements.txt
plain
Edit in files
•
Show inline
4. Create ECS Task Definition (ecs_task_definition.json)
Define the ECS task to run the Docker container in LocalStack.

ecs_task_definition.json
json
Edit in files
•
Show inline
Details:

Family: Unique task name.
Container: Uses the readmission-prediction image.
Port: Maps 8000 for API access.
Environment: Sets LocalStack and MLflow variables.
Health Check: Uses the /health endpoint.
Fargate: Simulates serverless ECS.
5. Create Deployment Script (deploy_ecs.sh)
Automate ECS cluster, service, and task deployment in LocalStack.

deploy_ecs.sh
x-shellscript
Edit in files
•
Show inline
Details:

Builds and pushes the Docker image to LocalStack’s ECR.
Creates an ECR repository, ECS cluster, and service.
Uses dummy subnet and security group IDs (valid for LocalStack).
6. Test Locally (Before ECS)
Verify the FastAPI app and Docker container locally.

Steps:

Save Files:
Save app.py, Dockerfile, requirements.txt, ecs_task_definition.json, and deploy_ecs.sh in C:\Users\GabrielF\patient-readmission-prediction.
Make deploy_ecs.sh executable (on Windows, use Git Bash or WSL):

chmod +x deploy_ecs.sh
Install Dependencies:

pip install -r requirements.txt
Start LocalStack:

docker run -d -p 4566:4566 -p 4510-4559:4510-4559 --env SERVICES=s3,ecr,ecs,cloudwatch --env HOSTNAME_EXTERNAL=localhost --env S3_PATH_STYLE=1 localstack/localstack
Start MLflow Server:

mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 127.0.0.1 --port 5000
Test FastAPI Locally:

cd C:\Users\GabrielF\patient-readmission-prediction
uvicorn app:app --host 0.0.0.0 --port 8000
Open http://127.0.0.1:8000/docs in a browser to view the Swagger UI.
Test /predict with a sample POST request (use curl or Swagger):

curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Expected response: {"readmission_probability": <float>}.
Stop Uvicorn with Ctrl+C.
Build and Test Docker Container:

docker build -t readmission-prediction:latest .
docker run -d -p 8000:8000 --env AWS_ENDPOINT_URL=http://host.docker.internal:4566 readmission-prediction:latest
Test /predict again:

curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Stop the container:

docker ps
docker stop <container_id>
7. Deploy to ECS (LocalStack)
Deploy the container to a simulated AWS ECS environment using LocalStack.

Steps:

Ensure LocalStack is Running (from Step 6.4).
Create LocalStack Network Resources:

awslocal ec2 create-vpc --cidr-block 10.0.0.0/16
awslocal ec2 create-subnet --vpc-id <vpc-id-from-above> --cidr-block 10.0.1.0/24
awslocal ec2 create-security-group --group-name readmission-sg --description "SG for readmission API" --vpc-id <vpc-id>
awslocal ec2 authorize-security-group-ingress --group-id <sg-id-from-above> --protocol tcp --port 8000 --cidr 0.0.0.0/0
Replace <vpc-id> and <sg-id> in deploy_ecs.sh with the actual IDs from the output.
Run Deployment Script (use Git Bash or WSL on Windows):

cd C:\Users\GabrielF\patient-readmission-prediction
./deploy_ecs.sh
Verify ECS Deployment:
Check ECS service:

awslocal ecs list-services --cluster readmission-cluster
awslocal ecs describe-services --cluster readmission-cluster --services readmission-service
Test the API (LocalStack forwards to port 8080):

curl -X POST "http://127.0.0.1:8080/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Expected: {"readmission_probability": <float>}.
