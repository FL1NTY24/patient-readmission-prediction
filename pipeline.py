import os
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://127.0.0.1:4566"
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ENDPOINT_URL"] = "http://127.0.0.1:4566"
os.environ["AWS_S3_FORCE_PATH_STYLE"] = "true"
from prefect import flow, task
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
import mlflow
import mlflow.sklearn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import os

@task
def configure_environment():
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_ENDPOINT_URL"] = "http://127.0.0.1:4566"
    os.environ["AWS_S3_FORCE_PATH_STYLE"] = "true"
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("PatientReadmission")

@task
def preprocess_data(data_path="data/diabetes_data.csv"):
    data = pd.read_csv(data_path)
    data = data.dropna(subset=["readmitted"])
    
    le = LabelEncoder()
    for col in ["race", "gender", "diabetesMed"]:
        if col in data.columns:
            data[col] = le.fit_transform(data[col].astype(str))
    
    if "age" in data.columns and data["age"].dtype == object:
        data["age"] = data["age"].str.extract(r'(\d+)-\d+').astype(float)
        if data["age"].isna().any():
            print("Warning: Some 'age' values could not be parsed. Filling with median age.")
            data["age"] = data["age"].fillna(data["age"].median())
    
    features = ["age", "gender", "race", "time_in_hospital", "num_lab_procedures", "num_medications", "diabetesMed"]
    missing_features = [f for f in features if f not in data.columns]
    if missing_features:
        raise ValueError(f"Missing columns in dataset: {missing_features}")
    
    X = data[features].fillna(0)
    y = (data["readmitted"] == "<30").astype(int)
    return X, y

@task
def train_model(X, y, params):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    return model, X_test, y_test

@task
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc_roc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred)
    
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    cm_path = "confusion_matrix.png"
    plt.savefig(cm_path)
    plt.close()
    
    return auc_roc, precision, recall, cm_path

@task
def log_to_mlflow(params, model, auc_roc, precision, recall, cm_path, X_sample):
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metric("auc_roc", auc_roc)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        X_sample_float = X_sample[:5].astype(np.float64)
        mlflow.sklearn.log_model(
            sk_model=model,
            name="random_forest_model",
            input_example=X_sample_float
        )
        mlflow.log_artifact(cm_path)
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/random_forest_model"
        mlflow.register_model(model_uri, "ReadmissionModel")

@flow(name="Patient Readmission Prediction Pipeline")
def readmission_pipeline(data_path="data/diabetes_data.csv"):
    configure_environment()
    X, y = preprocess_data(data_path)
    params = {"n_estimators": 100, "max_depth": 5, "random_state": 42, "class_weight": "balanced"}
    model, X_test, y_test = train_model(X, y, params)
    auc_roc, precision, recall, cm_path = evaluate_model(model, X_test, y_test)
    log_to_mlflow(params, model, auc_roc, precision, recall, cm_path, X_test)
    return auc_roc, precision, recall

if __name__ == "__main__":
    readmission_pipeline()