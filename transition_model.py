from mlflow.tracking import MlflowClient

client = MlflowClient(tracking_uri="http://127.0.0.1:5000")
client.transition_model_version_stage(
    name="ReadmissionModel",
    version=1,  # Replace with the correct version number from the UI
    stage="Production"
)