## Model Monitoring:

This section implements model monitoring using Evidently AI to generate data drift (e.g., age distribution shifts) and model performance (AUC-ROC, precision, recall) reports, saved to `s3://readmission-bucket/reports/`. A script (`monitor.py`) checks thresholds (drift score > 0.5 or AUC-ROC < 0.75) and triggers SNS alerts (simulated in LocalStack).

**Prerequisites**:

- Existing Setup:
  
  + MLflow server running at http://127.0.0.1:5000 with ReadmissionModel version 1 in Production and artifacts in s3://readmission-bucket/mlflow-artifacts/.
    
  + diabetes_data.csv in C:\Users\GabrielF\patient-readmission-prediction\data with columns: age, gender, race, time_in_hospital, num_lab_procedures, num_medications, diabetesMed, readmitted.
    
  + LocalStack running with SERVICES=s3,sns,cloudwatch (configured below).
    
  + Docker Desktop with WSL2 integration enabled.
    
  + Python 3.9.13 with dependencies installed (from previous steps: mlflow, pandas, scikit-learn).

  + Files: Save the provided monitor.py script in C:\Users\<rootuserfolder>\patient-readmission-prediction.

1. **Install Dependencies**:
   
- Install Evidently AI and boto3 for S3/SNS interactions:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  py -m pip install evidently==0.4.12 boto3==1.28.85 botocore==1.31.85
  ```
  
- Verify:
  ```powershell
  pip show evidently boto3 botocore
  ```
- Expected: evidently==0.4.12, boto3==1.28.85, botocore==1.31.85.

2. **Restart LocalStack with Required Services**:
   
- Ensure LocalStack includes s3, sns, and cloudwatch:
  ```powershell
  docker ps  # Note container ID
  docker stop <containerid>
  docker rm <containerid>
  ```
  
  ```powershell
  docker run -d -p 4566:4566 -p 4510-4559:4510-4559 `
  --network readmission-network `
  --network-alias localstack `
  --name localstack `
  --env SERVICES=s3,sns,cloudwatch `
  --env HOSTNAME_EXTERNAL=localhost.localstack.cloud `
  --env S3_PATH_STYLE=1 `
  --env DOCKER_HOST="tcp://host.docker.internal:2375" `
  --env MAIN_DOCKER_NETWORK=readmission-network `
  localstack/localstack:latest
  ```
  
- Wait 30-60 seconds, verify:
  ```powershell
  docker ps  # Status should be 'healthy'
  ```
  
3. **Set Environment Variables**:
  ```powershell
  $env:AWS_S3_FORCE_PATH_STYLE = "true"
  $env:AWS_ENDPOINT_URL = "http://127.0.0.1:4566"
  $env:GIT_PYTHON_REFRESH = "quiet"
  ```

4. **Recreate S3 Bucket and SNS Topic**:
   
- Since LocalStack state resets on restart, recreate resources:
  ```powershell
  awslocal s3 mb s3://readmission-bucket
  awslocal sns create-topic --name readmission-alerts
  ```
  
- Verify:
  ```powershell
  awslocal sns list-topics
  ```
  
- Expected: Lists arn:aws:sns:us-east-1:000000000000:readmission-alerts.

5. **Ensure MLflow Artifacts**:
   
- Check if model artifacts exist:
  ```powershell
  awslocal s3 ls s3://readmission-bucket/mlflow-artifacts/ --recursive
  ```
  
- If empty, restore artifacts:
- Reset MLflow and Rerun Pipeline:
- Stop MLflow Server: In the PowerShell tab running the MLflow server, press Ctrl+C to stop it. Close the browser tab with the MLflow UI (http://127.0.0.1:5000).
  
- Recreate mlflow.db:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  Remove-Item -Force mlflow.db -ErrorAction SilentlyContinue
  New-Item -ItemType File mlflow.db
  ```
  
- Restart MLflow Server:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  py -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 0.0.0.0 --port 5000
  ```
  
- Verifies: MLflow UI is accessible at http://127.0.0.1:5000.

- Test MLflow Server:
-Open a new windows powershell tab.
  ```powershell
  curl http://127.0.0.1:5000
  ```
  
6. **Run pipeline**:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  powershellpython pipeline.py
  ```

7. **Transition model**:
  ```powershell
  powershellpython transition_model.py
  ```

8. **Verify artifacts**:
  ```powershell
  awslocal s3 ls s3://readmission-bucket/mlflow-artifacts/ --recursive
  ```

-Expected: Files like mlflow-artifacts/1/<run_id>/artifacts/model.pkl.

9. **Run Monitoring Script**:
- Save monitor.py (from previous response) in C:\Users\<rootuserfolder>\patient-readmission-prediction and run:
  ```powershell
  $env:AWS_ACCESS_KEY_ID = "test"
  $env:AWS_SECRET_ACCESS_KEY = "test"
  $env:AWS_DEFAULT_REGION = "us-east-1"
  $env:AWS_S3_FORCE_PATH_STYLE = "true"
  $env:AWS_ENDPOINT_URL = "http://127.0.0.1:4566"
  $env:MLFLOW_S3_ENDPOINT_URL = "http://127.0.0.1:4566"
  python monitor.py
  ```
  
- Expected console output:
  + textData Drift Report saved to s3://readmission-bucket/reports/data_drift_report_<timestamp>.html
  + Model Performance Report saved to s3://readmission-bucket/reports/model_performance_report_<timestamp>.html
  + Alert: Data drift detected! Drift score: <score> exceeds threshold 0.5.
  + Alert: Model performance below threshold! AUC-ROC: <score> < 0.75.
  + Note: Alerts appear only if thresholds are violated (e.g., drift score > 0.5 or AUC-ROC < 0.75). The script simulates drift by shifting age values.


10. **Verify Reports in S3**
  ```powershell
  awslocal s3 ls s3://readmission-bucket/reports/ --recursive
  ```
- Expected: Lists reports/data_drift_report_<timestamp>.html and reports/model_performance_report_<timestamp>.html.
  
-Download a report (optional):
  ```powershell
  awslocal s3 cp s3://readmission-bucket/reports/data_drift_report_<timestamp>.html data_drift_report.html
  ```

- Open data_drift_report.html in a browser to view visualizations (e.g., age distribution drift).

11. **Verify SNS Alerts**:
    
- Since no subscriptions are set (simulated), check the console output for alert messages. To verify the topic:
  ```powershell
  awslocal sns list-topics
  ```
- Expected: Lists readmission-alerts.

**Troubleshooting:**
- Note: If `NotFoundException: Topic does not exist` occurs, verify the SNS topic ARN in `monitor.py` matches the output of:
  ```powershell
  awslocal sns list-topics
  ```
