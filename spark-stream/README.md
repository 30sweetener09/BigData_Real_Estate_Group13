
# Spark Streaming with Kafka and MongoDB

## Setup Instructions

### 1. Create Spark Namespace
```bash
minikube kubectl -- create namespace spark
```

### 2. Build Docker Image
First, ensure Docker is installed. Set up the Docker environment:
```bash
minikube -p minikube docker-env | Invoke-Expression
docker build -t spark-kafka-mongo:3.5.5.v1 .
```

For detailed Docker configuration and source code, see the [GitHub repository](https://github.com).

### 3. Deploy Spark Streaming Pod
```bash
minikube kubectl -- create deployment spark-stream --image=spark-kafka-mongo:3.5.5.v3 -n spark -- /bin/bash -c "sleep infinity"
```

### 4. Verify Pod Creation
```bash
minikube kubectl -- get pods -A
```

Note the pod name from the running spark-stream deployment.

### 5. Access Pod Bash Shell
```bash
minikube kubectl -- exec -it <POD_NAME> -n spark -- bash
```

Replace `<POD_NAME>` with your actual pod name (e.g., `spark-stream-59959cb66d-x48n4`).

### 6. Run Spark Streaming Job
Inside the pod bash, execute:
```bash
/opt/spark/bin/spark-submit \
    --master local[*] \
    --jars \
/tmp/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar,\
/tmp/jars/spark-token-provider-kafka-0-10_2.12-3.5.0.jar,\
/tmp/jars/kafka-clients-3.4.1.jar,\
/tmp/jars/commons-pool2-2.11.1.jar,\
/tmp/jars/lz4-java-1.8.0.jar,\
/tmp/jars/snappy-java-1.1.10.3.jar \
    /opt/spark/app/spark-kafka-streaming.py
```
