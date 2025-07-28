from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.sklearn
import pandas as pd
import numpy as np
import os

# Configure environment for LocalStack and MLflow
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_ENDPOINT_URL"] = "http://127.0.0.1:4566"
os.environ["AWS_S3_FORCE_PATH_STYLE"] = "true"
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
mlflow.set_tracking_uri("http://127.0.0.1:5000")

app = FastAPI(title="Patient Readmission Prediction API")

# Pydantic model for input validation
class PatientData(BaseModel):
       age: float
       gender: int
       race: int
       time_in_hospital: int
       num_lab_procedures: int
       num_medications: int
       diabetesMed: int

# Load the latest ReadmissionModel
try:
       model = mlflow.sklearn.load_model("models:/ReadmissionModel/Production")
except Exception as e:
       raise Exception(f"Failed to load model: {str(e)}")

@app.get("/health")
async def health_check():
       return {"status": "healthy"}

@app.post("/predict")
async def predict(data: PatientData):
       try:
           # Convert input to DataFrame
           input_data = pd.DataFrame([data.dict()], columns=[
               "age", "gender", "race", "time_in_hospital",
               "num_lab_procedures", "num_medications", "diabetesMed"
           ])
           # Ensure float64 for compatibility
           input_data = input_data.astype(np.float64)
           # Predict probability
           prob = model.predict_proba(input_data)[:, 1][0]
           return {"readmission_probability": float(prob)}
       except Exception as e:
           raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")