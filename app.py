import os
import mlflow
import mlflow.sklearn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Patient Readmission Prediction API")

# Set environment variables for LocalStack and MLflow
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://host.docker.internal:4566"
os.environ["AWS_ENDPOINT_URL"] = "http://host.docker.internal:4566"
os.environ["AWS_S3_FORCE_PATH_STYLE"] = "true"
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
os.environ["MLFLOW_TRACKING_URI"] = "http://host.docker.internal:5000"
mlflow.set_tracking_uri("http://host.docker.internal:5000")
logger.debug("Environment variables set")

class PatientData(BaseModel):
    age: float
    gender: float
    race: float
    time_in_hospital: float
    num_lab_procedures: float
    num_medications: float
    diabetesMed: float

# Load MLflow model
model = None
try:
    logger.debug("Loading MLflow model")
    model = mlflow.sklearn.load_model("models:/ReadmissionModel/Production")
    logger.debug("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    logger.warning("Continuing without model; /predict will be disabled")

@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint called")
    status = "healthy" if model else "unhealthy (model not loaded)"
    return {"status": status}

@app.post("/predict")
async def predict(data: PatientData):
    logger.debug("Predict endpoint called with data: %s", data.dict())
    if model is None:
        logger.error("Model not loaded")
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        input_data = pd.DataFrame([data.dict()])
        input_data = input_data.astype(np.float64)
        logger.debug(f"Input DataFrame: {input_data}")
        prob = model.predict_proba(input_data)[:, 1][0]
        logger.debug(f"Prediction probability: {prob}")
        return {"readmission_probability": float(prob)}
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
