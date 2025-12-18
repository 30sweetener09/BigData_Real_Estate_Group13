
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
