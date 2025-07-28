#!/bin/bash

   set -e

   # Environment variables
   export AWS_ACCESS_KEY_ID=test
   export AWS_SECRET_ACCESS_KEY=test
   export AWS_ENDPOINT_URL=http://localhost:4566
   export AWS_S3_FORCE_PATH_STYLE=true

   # Variables
   ECR_REPOSITORY=readmission-ecr
   IMAGE_NAME=readmission-prediction
   TAG=latest
   CLUSTER_NAME=readmission-cluster
   SERVICE_NAME=readmission-service
   SUBNET_ID=subnet-12345678  # Replace with actual subnet ID
   SECURITY_GROUP_ID=sg-12345678  # Replace with actual security group ID

   # Build Docker image
   echo "Building Docker image..."
   docker build -t $IMAGE_NAME:$TAG .

   # Create ECR repository
   echo "Creating ECR repository..."
   awslocal ecr create-repository --repository-name $ECR_REPOSITORY || echo "ECR repository already exists"

   # Tag and push Docker image to LocalStack ECR
   echo "Tagging and pushing image to ECR..."
   docker tag $IMAGE_NAME:$TAG localhost:4566/$ECR_REPOSITORY:$TAG
   docker push localhost:4566/$ECR_REPOSITORY:$TAG

   # Create ECS cluster
   echo "Creating ECS cluster..."
   awslocal ecs create-cluster --cluster-name $CLUSTER_NAME || echo "Cluster already exists"

   # Register task definition
   echo "Registering task definition..."
   awslocal ecs register-task-definition --cli-input-json file://ecs_task_definition.json

   # Create or update ECS service
   echo "Creating/updating ECS service..."
   awslocal ecs create-service \
       --cluster $CLUSTER_NAME \
       --service-name $SERVICE_NAME \
       --task-definition readmission-task \
       --desired-count 1 \
       --launch-type FARGATE \
       --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" || \
   awslocal ecs update-service \
       --cluster $CLUSTER_NAME \
       --service $SERVICE_NAME \
       --task-definition readmission-task \
       --desired-count 1

   echo "Deployment complete. Test the API at http://localhost:8080/predict"
