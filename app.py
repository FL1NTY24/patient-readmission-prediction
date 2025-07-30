import os
import mlflow
import mlflow.pyfunc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Set environment variables for LocalStack and MLflow
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://host.docker.internal:4566"
os.environ["AWS_ENDPOINT_URL"] = "http://host.docker.internal:4566"
os.environ["MLFLOW_TRACKING_URI"] = "http://host.docker.internal:5000"

class PredictionInput(BaseModel):
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
    model = mlflow.pyfunc.load_model("models:/ReadmissionModel/Production")
    logger.debug("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    logger.warning("Continuing without model; /predict will be disabled")

@app.get("/health")
async def health():
    return {"status": "healthy" if model else "unhealthy (model not loaded)"}

@app.post("/predict")
async def predict(data: PredictionInput):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    try:
        logger.debug(f"Received input: {data.dict()}")
        input_df = pd.DataFrame([data.dict()]).astype(float)
        logger.debug(f"Input DataFrame: {input_df}")
        prediction = model.predict(input_df)
        logger.debug(f"Prediction: {prediction}")
        return {"prediction": prediction.tolist()}
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")