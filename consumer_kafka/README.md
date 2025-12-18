
# Consumer Kafka

## Cài đặt và chạy Consumer

### 1. Cài đặt Docker CLI
```bash
choco install docker-cli
```

### 2. Kết nối Docker với Minikube
```bash
minikube -p minikube docker-env | Invoke-Expression
```

### 3. Xây dựng Docker Image
```bash
docker build -t my-consumer-app:v1 .
```

### 4. Tạo Deployment
```bash
minikube kubectl -- create deployment my-consumer --image=my-consumer-app:v1 -n kafka -- /bin/bash -c "sleep infinity"
```

### 5. Chờ Pod chạy
```bash
minikube kubectl -- get pods -w
```
Đợi trạng thái pod chuyển sang `Running`.

### 6. Chạy Consumer
```bash
minikube kubectl -- exec -it my-consumer-577bbb95dd-rncc5 -n kafka -- python3 /app/consumer.py
```

> **Lưu ý:** Thay `my-consumer-577bbb95dd-rncc5` bằng tên pod thực tế của bạn.
