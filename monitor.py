# monitor.py
import pandas as pd
import evidently
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
import boto3
import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.metrics import roc_auc_score
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import os

# Configuration
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"
AWS_DEFAULT_REGION = "us-east-1"
AWS_ENDPOINT_URL = "http://127.0.0.1:4566"
AWS_S3_FORCE_PATH_STYLE = "true"
MLFLOW_S3_ENDPOINT_URL = "http://127.0.0.1:4566"
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
S3_BUCKET = "readmission-bucket"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:000000000000:readmission-alerts"
DATA_PATH = "data/diabetes_data.csv"

# Set environment variables and MLflow tracking URI
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION
os.environ["AWS_ENDPOINT_URL"] = AWS_ENDPOINT_URL
os.environ["AWS_S3_FORCE_PATH_STYLE"] = AWS_S3_FORCE_PATH_STYLE
os.environ["MLFLOW_S3_ENDPOINT_URL"] = MLFLOW_S3_ENDPOINT_URL
os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Initialize boto3 clients for LocalStack
boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=AWS_ENDPOINT_URL
)
sns_client = boto3.client(
    "sns",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=AWS_ENDPOINT_URL
)

def load_data():
    """Load and split dataset into reference and current."""
    try:
        df = pd.read_csv(DATA_PATH)
        # Verify required columns
        required_columns = ["age", "gender", "race", "time_in_hospital", "num_lab_procedures", "num_medications", "diabetesMed", "readmitted"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in {DATA_PATH}: {missing_columns}")
        # Preprocess age column
        if df["age"].dtype == object:
            df["age"] = df["age"].str.extract(r'(\d+)-\d+').astype(float)
            df["age"] = df["age"].fillna(df["age"].median())
        # Encode categorical variables
        le = LabelEncoder()
        for col in ["race", "gender", "diabetesMed"]:
            if col in df.columns:
                df[col] = le.fit_transform(df[col].astype(str))
        # Split data
        ref_data = df.sample(frac=0.7, random_state=42)
        curr_data = df.drop(ref_data.index)
        # Simulate drift in current data (e.g., shift age)
        curr_data["age"] = curr_data["age"] + np.random.normal(5, 2, curr_data.shape[0])
        return ref_data, curr_data
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise

def generate_reports(ref_data, curr_data):
    """Generate data drift and model performance reports."""
    model = mlflow.sklearn.load_model("models:/ReadmissionModel/1")

    # Extract labels before selecting features
    ref_labels = ref_data["readmitted"].apply(lambda x: 1 if x == "<30" else 0)
    curr_labels = curr_data["readmitted"].apply(lambda x: 1 if x == "<30" else 0)

    ref_data = ref_data[["age", "gender", "race", "time_in_hospital", "num_lab_procedures", "num_medications", "diabetesMed"]]
    curr_data = curr_data[["age", "gender", "race", "time_in_hospital", "num_lab_procedures", "num_medications", "diabetesMed"]]

    # Data Drift Report
    drift_report = Report(metrics=[DataDriftPreset()])
    drift_report.run(reference_data=ref_data, current_data=curr_data)
    drift_score = drift_report.as_dict()["metrics"][0]["result"]["dataset_drift"]

    # Model Performance Report
    ref_preds = model.predict_proba(ref_data)[:, 1]
    curr_preds = model.predict_proba(curr_data)[:, 1]
    perf_report = Report(metrics=[ClassificationPreset()])
    perf_report.run(
        reference_data=ref_data.assign(target=ref_labels, prediction=ref_preds),
        current_data=curr_data.assign(target=curr_labels, prediction=curr_preds)
    )
    auc_roc = roc_auc_score(curr_labels, curr_preds)

    return drift_report, perf_report, drift_score, auc_roc

def save_reports(drift_report, perf_report):
    """Save reports to S3."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    drift_path = f"reports/data_drift_report_{timestamp}.html"
    perf_path = f"reports/model_performance_report_{timestamp}.html"
    
    drift_report.save_html("drift_report.html")
    perf_report.save_html("perf_report.html")
    
    s3_client.upload_file("drift_report.html", S3_BUCKET, drift_path)
    s3_client.upload_file("perf_report.html", S3_BUCKET, perf_path)
    
    print(f"Data Drift Report saved to s3://{S3_BUCKET}/{drift_path}")
    print(f"Model Performance Report saved to s3://{S3_BUCKET}/{perf_path}")

def check_thresholds_and_alert(drift_score, auc_roc):
    """Check thresholds and send SNS alerts if violated."""
    drift_threshold = 0.5
    auc_threshold = 0.75
    
    if drift_score:
        message = f"Alert: Data drift detected! Drift score: {drift_score:.3f} exceeds threshold {drift_threshold}."
        sns_client.publish(TopicArn=SNS_TOPIC_ARN, Message=message)
        print(message)
    
    if auc_roc < auc_threshold:
        message = f"Alert: Model performance below threshold! AUC-ROC: {auc_roc:.3f} < {auc_threshold}."
        sns_client.publish(TopicArn=SNS_TOPIC_ARN, Message=message)
        print(message)

def main():
    ref_data, curr_data = load_data()
    drift_report, perf_report, drift_score, auc_roc = generate_reports(ref_data, curr_data)
    save_reports(drift_report, perf_report)
    check_thresholds_and_alert(drift_score, auc_roc)

if __name__ == "__main__":
    main()