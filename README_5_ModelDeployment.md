## Model Deployment

Deploy the trained ReadmissionModel (Random Forest Classifier) as a REST API using FastAPI, containerize it with Docker, and deploy it to AWS ECS (simulated locally via LocalStack for cost-free testing). The deployment will enable real-time inference for patient readmission risk prediction and be accessible for testing.

**Prerequisites**:

- Existing Setup:

  + mlops_project.py and pipeline.py successfully train and log the ReadmissionModel to MLflow (tracking URI: http://127.0.0.1:5000, SQLite backend: sqlite:///mlflow.db, S3 artifacts: s3://readmission-bucket/mlflow-artifacts).

  + diabetes_data.csv (UCI Diabetes 130-Hospitals Dataset) is in C:\Users\<rootuserfolder>\patient-readmission-prediction\data.

  + LocalStack is running with S3, ECR, ECS, and CloudWatch services (ports 4566, 4510-4559).

  + Terraform scripts in infrastructure/ provision an S3 bucket (readmission-bucket) and SNS topic.

- Save Files:

  + Save app.py, Dockerfile, requirements.txt, ecs_task_definition.json, and deploy_ecs.sh in C:\Users\<rootuserfolder>\patient-readmission-prediction.

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

3. **Start LocalStack** (if not already running):
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  docker run -d -p 4566:4566 -p 4510-4559:4510-4559 --network readmission-network --network-alias localstack --name localstack --env SERVICES=s3,ecr,ecs,cloudwatch --env HOSTNAME_EXTERNAL=localstack --env S3_PATH_STYLE=1 localstack/localstack
  ```
- Verifies: LocalStack is running with S3, ECR, ECS, and CloudWatch services.

4. **Reset MLflow and Rerun Pipeline**:
- Stop MLflow Server: In the PowerShell tab running the MLflow server, press Ctrl+C to stop it. Close the browser tab with the MLflow UI (http://127.0.0.1:5000).

5. **Recreate mlflow.db**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  Remove-Item -Force mlflow.db -ErrorAction SilentlyContinue
  New-Item -ItemType File mlflow.db
  ```

6. **Restart MLflow Server**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  py -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 0.0.0.0 --port 5000
  ```

- Verifies: MLflow UI is accessible at http://127.0.0.1:5000.

7. **Test MLflow Server**:
  ```powershell
  curl http://127.0.0.1:5000
  ```

8. **Run Pipeline Script**:
  ```powershell
  python pipeline.py
  ```

9. **Run transition_model.py** (Update Model Version):

- Check the latest model version in the MLflow UI (http://127.0.0.1:5000/#/models).
- Update transition_model.py to set the latest version (Should be Version 1) to Production:
- Run:
  ```powershell
  python transition_model.py
  ```

10. **Verify Artifacts**:
  ```powershell
  awslocal s3 ls s3://readmission-bucket/mlflow-artifacts/ --recursive
  ```
11. **Check MLflow UI**:
- Open http://127.0.0.1:5000 in a browser. Confirm ReadmissionModel version 1 is in Production with the artifact path matching the pipeline.py output (e.g., s3://readmission-bucket/mlflow-artifacts/1/models/<new_model_id>/artifacts).
  
12. **Update app.py Model Version**:
    
- Edit line 24 in app.py to load the latest Production model version (e.g., 1):
- "pythonmodel = mlflow.sklearn.load_model("models:/ReadmissionModel/1")  # Update to latest version"

13. **Build the Image**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  docker build -t readmission-prediction:latest .
  ```

14. **Run Container with Correct Environment Variables**:
  ```powershell
  docker run -d -p 8000:8000 --network readmission-network --name fastapi --env AWS_ENDPOINT_URL=http://localstack:4566 --env MLFLOW_TRACKING_URI=http://host.docker.internal:5000 --env AWS_S3_FORCE_PATH_STYLE=true --env AWS_ACCESS_KEY_ID=test --env 
  AWS_SECRET_ACCESS_KEY=test --env AWS_DEFAULT_REGION=us-east-1 readmission-prediction:latest
  ```

15. **Get New Container ID**:
  ```powershell
  docker ps
  ```

16. **Test Connectivity from Container**:
  ```powershell
  docker exec -it <new_container_id> sh
  ```
  ```bash
  curl http://localstack:4566
  curl http://host.docker.internal:5000
  exit
  ```

17. **Test API Endpoints**:

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

18. **Stop Container** (after testing):
  ```powershell
  docker stop <new_container_id>
  docker rm <new_container_id>
  ```

19. **Deploy to ECS**:

- Run Deployment Script:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  wsl -d Ubuntu
  ```
  ```bash
  ./deploy_ecs.sh
  exit
  ```
  
- Verifies: Deployment completes with no errors.
- Test ECS Service:
  ```powershell
  curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d '{"age": 70.0, "gender": 1, "race": 2, "time_in_hospital": 5, "num_lab_procedures": 40, "num_medications": 15, "diabetesMed": 1}'
  ```
  
- Expected Output: {"readmission_probability": <float_value>}

20. **Troubleshooting** (if needed):

- Check ECS Service Status:
  ```powershell
  awslocal ecs describe-services --cluster readmission-cluster --services readmission-service
  ```
- Check Task Logs:
  ```powershellawslocal logs describe-log-streams --log-group-name readmission-logs
  awslocal logs get-log-events --log-group-name readmission-logs --log-stream-name <stream_name>
  ```
