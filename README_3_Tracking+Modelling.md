## Experiment Tracking and Model Registry

This section sets up MLflow to track experiments (logging parameters, metrics, and artifacts) and register the trained model, meeting the project’s experiment tracking and model registry requirements.

1. **Install MLflow and Dependencies**:
   ```powershell
   cd C:\Users\<rootuserfolder>
   py -m pip install mlflow scikit-learn pandas matplotlib seaborn
   ```
- Requirements:
  
  + mlflow==2.17.0
  
  + scikit-learn==1.2.2
  
  + pandas==1.5.3
  
  + matplotlib==3.7.5
  
  + seaborn==0.13.2

- Verify:
  ```powershell
  mlflow --version
  ```

2. **Start LocalStack (if not already running)**:

- Ensure LocalStack is running for S3 artifact storage:
   ```powershell
   docker ps
   docker run -d -p 4566:4566 -p 4510-4559:4510-4559 --env SERVICES=s3,sns --env HOSTNAME_EXTERNAL=localhost --env S3_PATH_STYLE=1 localstack/localstack
   ```

3. **Set Environment Variables**:

- Configure LocalStack for S3 access:
   ```powershell
   $env:AWS_S3_FORCE_PATH_STYLE = "true"
   $env:AWS_ENDPOINT_URL = "http://127.0.0.1:4566"
   ```


4. **Start MLflow Server**:

- Launch the MLflow server with a SQLite backend and LocalStack S3 artifact storage:
   ```powershell
   py -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://readmission-bucket/mlflow-artifacts --host 0.0.0.0 --port 5000
   ```
  ML Flow will launch locally on http://127.0.0.1:5000 - therefore, direct yourself to the following on a broswer of your choice - and then open a new tab on Windows Powershell to continue with the rest of the commands.

  **Don't close current Windows Powershell tab.**

5. **Run the Training Script**:

- All python scripts needed for this project can be found in the main github directory.
- Note: all scripts need to be downloaded and present in your local path: C:\Users\<rootuserfolder>\patient-readmission-prediction
- Execute the training script to log experiments and register the model:
   ```powershell
   cd C:\Users\<rootuserfolder>\patient-readmission-prediction
   python mlops_project.py
   ```

- Note: Ensure data/diabetes_data.csv (from UCI Diabetes 130-Hospitals Dataset) is in patient-readmission-prediction/data/. The script expects columns like age, gender, race, time_in_hospital, num_lab_procedures, num_medications, diabetesMed, readmitted. The age column (e.g., [70-80)) is converted to numeric. To verify columns:
  ```powershell
  python -c "import pandas as pd; print(pd.read_csv('data/diabetes_data.csv').columns)"
  ```

6. **Access MLflow UI**:
   
- Open http://127.0.0.1:5000 in a browser.
- Verify the "PatientReadmission" experiment with logged parameters (n_estimators, max_depth, random_state), metrics (auc_roc, precision, recall), and artifacts (random_forest_model, confusion_matrix.png).
- Check the "Models" tab for ReadmissionModel Version 1.

7. **Verify Artifacts in LocalStack**:
- Confirm MLflow artifacts are stored in S3:
   ```powershell
   awslocal s3 ls s3://readmission-bucket/mlflow-artifacts/ --recursive
   ```
