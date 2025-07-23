# ML OPS Project

Smart Healthcare: Predicting Patient Readmission Risk

# Problem Description:

Hospital readmissions for diabetic patients are a significant challenge, driven by factors such as disease complexity, limited health literacy, social determinants, and healthcare system inefficiencies. These readmissions increase costs and adversely affect patient outcomes, with billions spent annually in the U.S. alone. To address this, I developed a machine learning model to predict the likelihood of a diabetic patient being readmitted within 30 days, using features like age, medical history, diagnoses, and hospital stay details from the UCI Diabetes 130-Hospitals Dataset. The model is deployed as a web service, enabling clinicians and hospital administrators to identify high-risk patients and prioritize preventive interventions, ultimately improving care and reducing costs.

# Dataset: 

Data folder in directory contians all relevant data.

https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008

The dataset represents ten years (1999-2008) of clinical care at 130 US hospitals and integrated delivery networks. Each row concerns hospital records of patients diagnosed with diabetes, who underwent laboratory, medications, and stayed up to 14 days. The goal is to determine the early readmission of the patient within 30 days of discharge. The problem is important for the following reasons. Despite high-quality evidence showing improved clinical outcomes for diabetic patients who receive various preventive and therapeutic interventions, many patients do not receive them. This can be partially attributed to arbitrary diabetes management in hospital environments, which fail to attend to glycemic control. Failure to provide proper diabetes care not only increases the managing costs for the hospitals (as the patients are readmitted) but also impacts the morbidity and mortality of the patients, who may face complications associated with diabetes.

# Key Components:

Problem Statement:
I defined the challenge of hospital readmissions, focusing on their financial and health impacts. The model predicts readmission risk using patient data (demographics, medical history, hospital stay details) to prioritize interventions.

Dataset:
I used the UCI Diabetes 130-Hospitals Dataset, featuring patient demographics, medical history, and a binary readmission label.

Cloud Infrastructure:
I set up a cost-free infrastructure using LocalStack for local testing and AWS Free Tier for deployment. Using Terraform, I provisioned an S3 bucket for data/model storage, an EC2 t2.micro instance for MLflow (optional), an ECS cluster for FastAPI, and SNS for alerts. I tested locally with LocalStack and deployed to AWS for the final demo, terminating resources to avoid costs.

Experiment Tracking:
I implemented MLflow with a local SQLite backend to track experiments, logging Random Forest hyperparameters (e.g., n_estimators, max_depth), metrics (AUC-ROC, precision, recall), and artifacts (model, confusion matrix). The best model is registered in the MLflow Model Registry.

Workflow Orchestration:
I built a Prefect pipeline to automate data preprocessing, model training, evaluation, and deployment to FastAPI (if AUC-ROC > 0.75). The pipeline runs locally with Prefect’s free-tier cloud for visualization and is scheduled for daily retraining.

Model Training:
I trained a Random Forest Classifier using scikit-learn on the dataset (saved as diabetes_data.csv). The training pipeline is integrated with Prefect and MLflow for seamless execution and tracking.

Model Deployment:
I deployed a FastAPI web service in a Docker container on AWS ECS (free tier). The API, defined in api.py, serves predictions and is tested locally with Docker before deployment. Usage instructions are provided in the README.

Model Monitoring:
I used Evidently AI to generate data drift and performance reports (e.g., AUC-ROC, patient age distribution shifts), saved to S3 (simulated via LocalStack). A script (monitor.py) triggers SNS alerts for drift thresholds.

Reproducibility:
I ensured reproducibility with a requirements.txt pinning dependencies (e.g., pandas==1.5.3, scikit-learn==1.2.2), a detailed README with setup and execution instructions, and a public GitHub repository.

Best Practices:
I implemented unit and integration tests with pytest, enforced code style with black and flake8, and used pre-commit hooks for consistency. A Makefile simplifies commands, and GitHub Actions handles CI/CD for automated testing and deployment.

Note:
All commands presented were ran on windows powershell.
