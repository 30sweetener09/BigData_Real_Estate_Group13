
# MongoDB Setup Guide

## Prerequisites
For Helm installation details, refer to section 2 (Hadoop) in the main documentation.

## Installation Steps

### 1. Update Bitnami Repository
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### 2. Install MongoDB
```bash
helm install my-mongodb bitnami/mongodb
```

### 3. Verify Pod Status
```bash
kubectl get pods
```

## Retrieve Root Password

### Extract Encoded Password
```powershell
$EncodedPassword = minikube kubectl -- get secret --namespace default my-mongodb -o jsonpath="{.data.mongodb-root-password}"
```

### Decode Base64 and Set Environment Variable
```powershell
$env:MONGODB_ROOT_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($EncodedPassword))
```

### Verify Password
```powershell
echo $env:MONGODB_ROOT_PASSWORD
```
#

# MongoDB Role and Data Flow in Big Data Real Estate System

### 1. Role of MongoDB

In the Big Data Real Estate project, MongoDB is used as the serving data store.
Its main purpose is to store processed and aggregated data that are ready for querying and analysis.

MongoDB is not used for raw data storage or large-scale batch storage.
Those responsibilities belong to the distributed storage layer.

### 2. Data Types Stored in MongoDB

MongoDB stores:
- Cleaned real estate listings
- Aggregated statistics such as average prices, transaction counts, or trends
- Data prepared for visualization and reporting

MongoDB does not store:
- Raw input data
- Intermediate processing data
- Historical backups

### 3. Data Flow Overview

The data flow related to MongoDB can be summarized as follows:

- Raw data is ingested into the system through the data ingestion layer
- Data is processed and transformed by the data processing layer
- Processed results are written into MongoDB
- Visualization or analysis components read data directly from MongoDB

MongoDB acts as the final data access layer for users and dashboards.

### 4. Access Pattern

MongoDB is mainly accessed in read-heavy scenarios.
Write operations are performed periodically after data processing jobs complete.
Real-time write operations are limited in the current implementation.

### 5. Design Considerations

MongoDB was chosen because:
- It provides flexible schema design
- It supports JSON-like document structures
- It is suitable for fast read access in analytics use cases

The current deployment focuses on simplicity and functional correctness rather than high availability or performance optimization.

### 6. Current Limitations

- MongoDB is deployed as a single instance
- No replication or sharding is configured
- Index optimization is not applied
- Scalability improvements are left for future work
