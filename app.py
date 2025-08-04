import os
import logging
import mlflow.sklearn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

app = FastAPI()
model = None

class PatientData(BaseModel):
       age: float
       gender: float
       race: float
       time_in_hospital: float
       num_lab_procedures: float
       num_medications: float
       diabetesMed: float

@app.on_event("startup")
async def startup_event():
    global model
    logger.debug("Environment variables set")
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_ENDPOINT_URL"] = "http://localstack:4566"
    os.environ["AWS_S3_FORCE_PATH_STYLE"] = "true"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localstack:4566"
    os.environ["MLFLOW_TRACKING_URI"] = "http://host.docker.internal:5000"
    mlflow.set_tracking_uri("http://host.docker.internal:5000")
    try:
        logger.debug("Loading MLflow model")
        model = mlflow.sklearn.load_model("models:/ReadmissionModel/1")
        logger.debug("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}", exc_info=True)
        logger.warning("Continuing without model; /predict will be disabled")

@app.get("/health")
async def health_check():
       logger.debug("Health check endpoint called")
       return {"status": "healthy" if model is not None else "unhealthy (model not loaded)"}

@app.post("/predict")
async def predict(data: PatientData):
       logger.debug(f"Predict endpoint called with data: {data.dict()}")
       if model is None:
           logger.error("Model not loaded")
           raise HTTPException(status_code=503, detail="Model not loaded")
       input_data = [[
           data.age, data.gender, data.race, data.time_in_hospital,
           data.num_lab_procedures, data.num_medications, data.diabetesMed
       ]]
       prediction = model.predict_proba(input_data)[0][1]
       return {"readmission_probability": float(prediction)}