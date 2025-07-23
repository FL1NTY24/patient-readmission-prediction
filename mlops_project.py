import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import os

# Set MLflow tracking URI and artifact location
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_ENDPOINT_URL"] = "http://127.0.0.1:4566"
os.environ["AWS_S3_FORCE_PATH_STYLE"] = "true"
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("PatientReadmission")

# Load and preprocess data
data = pd.read_csv("data/diabetes_data.csv")
# Basic preprocessing (example, adjust based on dataset)
data = data.dropna(subset=["readmitted"])  # Drop rows with missing target
# Encode categorical variables
le = LabelEncoder()
for col in ["gender", "race", "diabetesMed"]:
    if col in data.columns:
        data[col] = le.fit_transform(data[col].astype(str))
# Select features and target
features = ["age", "gender", "race", "time_in_hospital", "num_lab_procedures", "num_medications", "diabetesMed"]
X = data[features].fillna(0)
y = (data["readmitted"] == "<30").astype(int)  # Binary: readmitted <30 days

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train and log model
with mlflow.start_run():
    # Define hyperparameters
    params = {"n_estimators": 100, "max_depth": 5, "random_state": 42}
    mlflow.log_params(params)
    
    # Train Random Forest
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # Predict and evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc_roc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    
    # Log metrics
    mlflow.log_metric("auc_roc", auc_roc)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    
    # Log model
    mlflow.sklearn.log_model(model, "random_forest_model")
    
    # Create and log confusion matrix plot
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    cm_path = "confusion_matrix.png"
    plt.savefig(cm_path)
    plt.close()
    mlflow.log_artifact(cm_path)
