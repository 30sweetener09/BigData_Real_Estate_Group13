# Kafka Producer Setup Guide

## Prerequisites
- Minikube installed and running
- Docker installed
- Python 3 with Kafka dependencies

## Build Docker Image

```bash
minikube -p minikube docker-env | Invoke-Expression
docker build -t my-producer-app:v1 .
```

## Deploy Producer Pod

Create a Kubernetes deployment with the producer image:

```bash
minikube kubectl -- create deployment my-producer \
    --image=my-producer-app:v1 \
    -n kafka \
    -- /bin/bash -c "sleep infinity"
```

## Run Producer

Execute the producer script inside the pod:

```bash
minikube kubectl -- exec -it my-producer-6d5d89b7dd-sqzcn \
    -n kafka \
    -- python3 /app/producer.py
```

**Note:** Replace `my-producer-6d5d89b7dd-sqzcn` with your actual pod name. Get it with:
```bash
minikube kubectl -- get pods -n kafka
```