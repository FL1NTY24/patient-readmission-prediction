## Workflow Orchestration

This step involves creating a Prefect flow to automate the ML pipeline from mlops_project.py (data preprocessing, model training, and MLflow logging) and ensuring integration with the existing setup (LocalStack S3 bucket readmission-bucket and MLflow server).

**Prerequisites**:

- Existing Setup:
  
  + mlops_project.py successfully logs parameters, metrics, artifacts, and registers the ReadmissionModel in MLflow.
  
  + MLflow server runs at http://127.0.0.1:5000 with SQLite backend (sqlite:///mlflow.db) and LocalStack S3 artifact storage (s3://readmission-bucket/mlflow-artifacts).
  
  + diabetes_data.csv is in C:\Users\<rootuserfolder>\patient-readmission-prediction\data.
  
  + LocalStack is running with readmission-bucket for S3 storage.

1. **Install Prefect**:
   
- Install Prefect in your Python environment.
  ```powershell
  cd C:\Users\<rootuserfolder>
  py -m pip uninstall prefect griffe -y
  py -m pip install prefect==2.14.0 griffe==0.25.0
  ```

- Verify installation:
  ```powershell
  prefect --version
  ```
  Expected: 2.14.0.

2. **Verify MLflow and LocalStack Setup**
   
- Ensure the MLflow server and LocalStack are running to support the Prefect flow.

- Start MLflow Server (if not running):
  ```powershell
  mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 127.0.0.1 --port 5000
  ```
  Verify: Open http://127.0.0.1:5000 in a browser to see the MLflow UI.

- Start LocalStack (if not running):
  ```powershell
  docker ps
  docker run -d -p 4566:4566 -p 4510-4559:4510-4559 --env SERVICES=s3,sns --env HOSTNAME_EXTERNAL=localhost --env S3_PATH_STYLE=1 localstack/localstack
  ```
- Set Environment Variables:
  ```powershell
  $env:AWS_S3_FORCE_PATH_STYLE = "true"
  $env:AWS_ENDPOINT_URL = "http://127.0.0.1:4566"
  ```
- Verify S3 Bucket:
  ```powershell
  awslocal s3 ls s3://readmission-bucket/
   ```
  Expected: PRE data/ PRE mlflow-artifacts/.

- Silence Git Warning (optional, for cleaner logs):
  ```powershell
  $env:GIT_PYTHON_REFRESH = "quiet"
  ```

3. **Create pipeline.py**:
   
- Needed to orchestrate the ML pipeline, modularizing the preprocessing, training, evaluation, and MLflow logging from mlops_project.py.
- Script can be found in the main github directory.
- Be sure to save the script with mlops_project.py in C:\Users\<rootuserfolder>\patient-readmission-prediction.

4. **Start the Prefect server**:
  ```powershell
  prefect server start
  ```
- Expected: Server starts, and you can access the Prefect UI at http://127.0.0.1:4200.
- Open a **new** PowerShell terminal to keep the server running.
  
5. **Run the Prefect Flow**:
   
- Execute pipeline.py to run the orchestrated pipeline.
- Ensure MLflow server and LocalStack are running (from Step 2).
- Run the flow:
  ```powershell
  cd C:\Users\<rootuserfolder>\patient-readmission-prediction
  python pipeline.py
  ```

- Monitor execution in the Prefect UI (http://127.0.0.1:4200). Expect a flow run named “Patient Readmission Prediction Pipeline” with tasks (configure_environment, etc.) marked as completed.

6. **Verify Outputs**:

- Confirm the pipeline logged to MLflow and stored artifacts in LocalStack.
- Steps:
  MLflow UI: Open http://127.0.0.1:5000.
  
  Check the “PatientReadmission” experiment for a new run with:
  
  + Parameters: n_estimators=100, max_depth=5, random_state=42.
  
  + Metrics: auc_roc, precision, recall.
  
  + Artifacts: random_forest_model, confusion_matrix.png.
  
  + Model: ReadmissionModel (new version, e.g., Version 2) in the “Models” tab.
  
- LocalStack S3:
  ```powershell
  awslocal s3 ls s3://readmission-bucket/mlflow-artifacts/ --recursive
  ```
  Expected: New artifacts under mlflow-artifacts/1/ (or a new experiment ID) with confusion_matrix.png and model files (model.pkl, etc.).
  
- Prefect UI: Open http://127.0.0.1:4200.
  Verify the flow run completed successfully with all tasks (preprocessing, training, etc.) marked as completed.

7. **To schedule daily runs (OPTIONAL)**:
  ```powershell
  prefect deployment build pipeline.py:readmission_pipeline -n readmission-pipeline -i "interval 86400"
  prefect deployment apply readmission_pipeline-deployment.yaml
  prefect agent start
  ```
