## Model Deployment

Deploy the trained ReadmissionModel (Random Forest Classifier) as a REST API using FastAPI, containerize it with Docker, and deploy it to AWS ECS (simulated locally via LocalStack for cost-free testing). The deployment will enable real-time inference for patient readmission risk prediction and be accessible for testing.

**Prerequisites**:

- Existing Setup:

  + mlops_project.py and pipeline.py successfully train and log the ReadmissionModel to MLflow (tracking URI: http://127.0.0.1:5000, SQLite backend: sqlite:///mlflow.db, S3 artifacts: s3://readmission-bucket/mlflow-artifacts).

  + diabetes_data.csv (UCI Diabetes 130-Hospitals Dataset) is in C:\Users\<rootuserfolder>\patient-readmission-prediction\data.

  + LocalStack is running with S3, ECR, ECS, CloudWatch, Logs, and EC2 services (ports 4566, 4510-4559).

- Save Files:

  + Save app.py, Dockerfile, and requirements.txt in C:\Users<rootuserfolder>\patient-readmission-prediction.

1. **Make deploy_ecs.sh Executable**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  ```
  ```bash
  wsl -d Ubuntu
  chmod +x deploy_ecs.sh
  ```

- Verify:
  ```bash
  ls -l deploy_ecs.sh
  ```
- Expected Output: -rwxrwxrwx

- Exit WSL:
  ```bash
  exit
  ```

2. **Install Dependencies**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  py -m pip install fastapi==0.99.1 uvicorn==0.30.6
  ```

- Verifies: fastapi==0.99.1, uvicorn==0.30.6.

3. **Restart LocalStack**:
- Stop and Remove LocalStack Container:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  docker ps
  docker stop <containerid>
  docker rm <containerid>
  ```
- Restart LocalStack on readmission-network:
  ```powershell
  docker run -d -p 4566:4566 -p 4510-4559:4510-4559 `
  --network readmission-network `
  --network-alias localstack `
  --name localstack `
  --env SERVICES=s3,ecs,cloudwatch,logs,ec2 `
  --env HOSTNAME_EXTERNAL=localstack `
  --env S3_PATH_STYLE=1 `
  localstack/localstack
  ```
  
- Verify Network:
  ```powershell
  docker network inspect readmission-network
  ```
- Look for:

  "Name": "localstack",

- Note: If ECR or ECS APIs fail due to LocalStack free-tier limitations, the deployment can be tested locally (see below).

4. **Recreate S3 Bucket** Since restarting LocalStack may reset its state:
  ```powershell
  awslocal s3 mb s3://readmission-bucket
  ```

5. **Reset MLflow and Rerun Pipeline**:
- Stop MLflow Server: In the PowerShell tab running the MLflow server, press Ctrl+C to stop it. Close the browser tab with the MLflow UI (http://127.0.0.1:5000).

6. **Recreate mlflow.db**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  Remove-Item -Force mlflow.db -ErrorAction SilentlyContinue
  New-Item -ItemType File mlflow.db
  ```

7. **Restart MLflow Server**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  py -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 0.0.0.0 --port 5000
  ```

- Verifies: MLflow UI is accessible at http://127.0.0.1:5000.

8. **Test MLflow Server**:
- Open a new windows powershell tab.
  ```powershell
  curl http://127.0.0.1:5000
  ```

9. **Run Pipeline Script**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  python pipeline.py
  ```

10. **Run transition_model.py** (Update Model Version):

- Check the latest model version in the MLflow UI (http://127.0.0.1:5000/#/models).
- Update transition_model.py to set the latest version (Should be Version 1) to Production:
- Run:
  ```powershell
  python transition_model.py
  ```

11. **Verify Artifacts**:
  ```powershell
  awslocal s3 ls s3://readmission-bucket/mlflow-artifacts/ --recursive
  ```
12. **Check MLflow UI**:
- Open http://127.0.0.1:5000 in a browser. Confirm ReadmissionModel version 1 is in Production with the artifact path matching the pipeline.py output (e.g., s3://readmission-bucket/mlflow-artifacts/1/models/<new_model_id>/artifacts).
  
13. **Update app.py Model Version**:
    
- Edit line 36 in app.py to load the latest Production model version (e.g., 1):
- "model = mlflow.sklearn.load_model("models:/ReadmissionModel/1")"

14. **Build the Image**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  docker build -t readmission-prediction:latest .
  ```

15. **Run Container with Correct Environment Variables**:
  ```powershell
  docker run -d -p 8000:8000 --network readmission-network --name fastapi --env AWS_ENDPOINT_URL=http://localstack:4566 --env MLFLOW_TRACKING_URI=http://host.docker.internal:5000 --env AWS_S3_FORCE_PATH_STYLE=true --env AWS_ACCESS_KEY_ID=test --env AWS_SECRET_ACCESS_KEY=test --env AWS_DEFAULT_REGION=us-east-1 readmission-prediction:latest
  ```

16. **Get New Container ID**:
  ```powershell
  docker ps
  ```

17. **Test Connectivity from Container**:
  ```powershell
  docker exec -it <new_container_id> sh
  ```
  ```bash
  curl http://localstack:4566
  curl http://host.docker.internal:5000
  exit
  ```

- Test Connectivity from Host (Optional):
  ```powershell
  curl http://127.0.0.1:4566  # LocalStack root endpoint
  curl http://127.0.0.1:5000  # MLflow UI
  ```
  
- Expected: Responses from LocalStack and MLflow UI HTML.

18. **Test API Endpoints**:

- Health Endpoint:
  ```powershell
  Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET
  ```
- Expected Output: {"status": "healthy"}
- Predict Endpoint:
  ```powershell
  Invoke-WebRequest -Uri "http://127.0.0.1:8000/predict" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
  ```
- Expected Output: {"readmission_probability": <float_value>} (e.g., {"readmission_probability": 0.5325880099359565})

19. **Stop Container** (after testing):
  ```powershell
  docker stop <new_container_id>
  docker rm <new_container_id>
  ```

**Cloud Deployment Note**:

Due to limitations in LocalStack's free tier, which does not fully support ECS and ECR APIs, the deployment was performed locally. The container is fully prepared for AWS ECS deployment in the Free Tier. The `ecs_task_definition.json` is configured for FARGATE with `awsvpc` networking (VPC: vpc-2bebeebf4675a6cb1, subnet: subnet-ee5741f3c6ebcfafd, security group: sg-9877088a8a7fe72fa). To deploy to AWS ECS, push the image to an AWS ECR repository, update `ecs_task_definition.json` with the ECR URI, and apply the Terraform scripts in `infrastructure/` with `localstack_enabled=false` and valid AWS credentials.

**Troubleshooting** (if needed):

- Check ECS Service Status:
  ```powershell
  awslocal ecs describe-services --cluster readmission-cluster --services readmission-service
  ```
- Check Task Logs:
  ```powershell
  awslocal logs get-log-events --log-group-name readmission-logs --log-stream-name <stream_name>
  ```
