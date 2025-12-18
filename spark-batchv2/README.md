## Environment Requirements

To ensure compatibility, the following system environment is required:

| Component     | Version   |
| :------------- | :---------- |
| **Minikube** | `v1.37.0`   |
| **Java** | `11.0.29`   |
| **Hadoop** | `3.4.2`     |
| **Spark** | `3.5.7`     |
| **Scala** | `2.12.18`   |
| **Python** | `3.9+`      |

---

## 📦 Python Dependencies

Install the necessary Python libraries on your local machine (Driver node) before execution:
```bash
pip install -r requirements.txt
```
---
## Execution Workflow & Results

1. Infrastructure Initialization (Minikube)
```bash
minikube start --driver=docker --memory=6144 --cpus=4 --disk-size=20g
kubectl get nodes
```

2. Deploy MongoDB on Kubernetes

Processed data will be stored in a MongoDB instance running within the data namespace.
```bash
kubectl create namespace data
kubectl create deployment mongo --image=mongo:6  -n data

# Expose port for Spark connectivity
kubectl expose deployment mongo --type=NodePort --port=27017 -n data 

# Monitor Pod status until it reaches 'Running'
kubectl get pods -n data -w 
```

To view service details or describe the pod for debugging:
```bash
minikube service mongo -n data 
kubectl describe pod $(kubectl get pods -n data -l app=mongo -o jsonpath='{.items[0].metadata.name}') -n data
```
3. Data Preparation on HDFS
```bash
# Start local Hadoop services
start-dfs.sh
start-yarn.sh

hdfs dfs -mkdir -p /data/nhatot
hdfs dfs -put path_to_your_data_lines.json /data/nhatot ## Đẩy file dữ liệu từ máy local lên HDFS
hdfs dfs -ls /data/nhatot ## Kiểm tra file đã tồn tại trên HDFS chưa
```

4. Execute Spark Batch Job (ETL)
```bash
spark-submit --master "local[*]"  --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.2 batching/spark_batch/spark_job.py
```

5. Verification in MongoDB
```bash
kubectl exec -it $(kubectl get pods -n data -l app=mongo -o jsonpath='{.items[0].metadata.name}') -n data -- mongosh real_estate
```

Run the following queries inside the mongosh terminal:
```bash
real_estate> db.properties.countDocuments();
real_estate> db.properties.find().limit(2).pretty();
```