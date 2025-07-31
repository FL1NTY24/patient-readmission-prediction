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

cd C:\Users\<rootuserfolder>
py -m pip install fastapi==0.99.1 uvicorn==0.30.6
Verifies: fastapi==0.99.1 uvicorn==0.30.6.
Start LocalStack (if not already running):

cd C:\Users\<rootuserfolder>\patient-readmission-prediction

docker run -d -p 4566:4566 -p 4510-4559:4510-4559 --env SERVICES=s3,ecr,ecs,cloudwatch --env HOSTNAME_EXTERNAL=localhost --env S3_PATH_STYLE=1 localstack/localstack
Verifies: LocalStack is running with S3, ECR, ECS, and CloudWatch services.
Start MLflow Server (If not running already):

py -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 0.0.0.0 --port 5000
Verifies: MLflow UI is accessible at http://127.0.0.1:5000.

Run transition_model - make sure the latest model version is correct in script (model version found at: http://127.0.0.1:5000/#/models)

python transition_model.py

Change app.py - line 24

    model = mlflow.pyfunc.load_model("models:/ReadmissionModel/8")

    the number 8 must be the latest version of the ml model.


Test FastAPI Locally:

uvicorn app:app --host 0.0.0.0 --port 8000
Open http://127.0.0.1:8000/docs in a browser to view the Swagger UI.
Open a new powershell tab.
Test the /predict endpoint:

cd C:\Users\<rootuserfolder>\patient-readmission-prediction
Invoke-WebRequest -Uri "http://127.0.0.1:8000/predict" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
Expected Output: {"readmission_probability": <float>} (e.g., {"readmission_probability": 0.73})
Test the /health endpoint:

Invoke-WebRequest -Uri "http://127.0.0.1:8000/health"
Expected Output: {"status": "healthy"}

On previous tab.
Stop Uvicorn with Ctrl+C.

Stop and Remove MLflow Container (if running):
docker stop mlflow
docker rm mlflow

Create a New mlflow.db:
cd C:\Users\GabrielF\patient-readmission-prediction
Remove-Item -Force mlflow.db -ErrorAction SilentlyContinue
New-Item -ItemType File mlflow.db

Close any previous MLFlow runs with ctrl+C

Run MLflow Server on Host:
py -m mlflow server `
--backend-store-uri sqlite:///mlflow.db `
--default-artifact-root s3://readmission-bucket/mlflow-artifacts `
--host 0.0.0.0 --port 5000

Test MLflow on Host:
curl http://127.0.0.1:5000

New Windows Tab

Run Pipeline Scripts:
cd C:\Users\GabrielF\patient-readmission-prediction
python pipeline.py
python transition_model.py (change model version to 1)

Verify Artifacts:
awslocal s3 ls s3://readmission-bucket/mlflow-artifacts/ --recursive

Check MLflow UI:

Open http://127.0.0.1:5000 in a browser.
Confirm ReadmissionModel version 1 is in Production with the correct artifact path (e.g., s3://readmission-bucket/mlflow-artifacts/1/models/m-<new_id>/artifacts/).

Update app.py model number

Build the Image:
cd C:\Users\GabrielF\patient-readmission-prediction
docker build -t readmission-prediction:latest .

Run Container with Correct Environment Variables:
docker run -d -p 8000:8000 `
--network readmission-network `
--env AWS_ENDPOINT_URL=http://host.docker.internal:4566 `
--env MLFLOW_TRACKING_URI=http://host.docker.internal:5000 `
--env AWS_S3_FORCE_PATH_STYLE=true `
--env AWS_ACCESS_KEY_ID=test `
--env AWS_SECRET_ACCESS_KEY=test `
--env AWS_DEFAULT_REGION=us-east-1 `
readmission-prediction:latest

Get New Container ID:
docker ps

Test Connectivity from Container:
docker exec -it <new_container_id> sh
Then:
curl http://host.docker.internal:4566
curl http://host.docker.internal:5000


Exit the shell:
exit

Test API Endpoints

Health Endpoint:
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET

Expected Output:
{"status": "healthy"}



Predict Endpoint:
Invoke-WebRequest -Uri "http://127.0.0.1:8000/predict" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'

Expected Output:
{"readmission_probability": <float_value>}
