
# Spark Batch Processing

## Build Docker Image

```bash
minikube -p minikube docker-env | Invoke-Expression
docker build -t spark-hdfs-mongo:3.5.5.v1 .
```

## Create Deployment

```bash
minikube kubectl -- create deployment spark-batch --image=spark-hdfs-mongo:3.5.5.v1 -n spark -- /bin/bash -c "sleep infinity"
```

## Run Spark Job

```bash
minikube kubectl -- exec -it <POD_NAME> -n spark -- /opt/spark/bin/spark-submit /opt/spark/app/spark-batch.py
```

### Get Pod Name

```bash
minikube kubectl -- get pods -n spark
```

Replace `<POD_NAME>` with the actual pod name from the output above.
