# 📊 Visualization Module
Module này chịu trách nhiệm xây dựng hạ tầng lưu trữ (MongoDB) và trực quan hóa dữ liệu (Metabase) chạy trên nền tảng **Kubernetes (Minikube)**.
## 📂 Cấu trúc thư mục visualization

| Tên file | Mô tả |
| :--- | :--- |
| **`dashboard-deployment.yaml`** | File cấu hình Kubernetes (Triển khai MongoDB Service & Metabase Service). |
| **`test_dashboard.py`** | Script Python đa năng: Nạp dữ liệu giả lập (Mock) hoặc Xóa sạch Database (Clean). |
| **`Guide.md`** | Tài liệu hướng dẫn. |

---
## 🛠️ Yêu cầu cài đặt (Prerequisites)

Để chạy được module này máy cần cài đặt:
- **Minikube**
- **Kubectl**
- **Python 3.x**
- Thư viện Python:
```bash
pip install pymongo
```

## 🚀 Hướng dẫn triển khai
### 1. Khởi động Hạ tầng
Mở Terminal tại thư mục `visualization`:

```bash
# Khởi động Minikube
minikube start

# Triển khai hệ thống
kubectl apply -f dashboard-deployment.yaml

# Kiểm tra (Chờ status là 'Running')
kubectl get pods
```
---

### 2. Thiết lập kết nối
Mở 2 terminal và giữ chúng luôn chạy:

#### Terminal A: Dùng để nạp dữ liệu vào MongoDB - Port 27017
```bash
kubectl port-forward service/mongodb-service 27017:27017
```
Nếu chạy dữ liệu giả lập, mở 1 terminal khác để chạy test_dashboard.py
```bash
# Để nạp dữ liệu giả vào MongoDB
py test_dashboard.py

# Để xóa sạch dữ liệu trong MongoDB trước khi Spark
py import_to_mongo.py clean
```

#### Terminal B: Dùng để truy cập Web Metabase
Gõ lệnh:
```bash
minikube service metabase-service
```
Nó sẽ tự bật trình duyệt lên một địa chỉ kiểu http://127.0.0.1:xxxxx (Cổng ngẫu nhiên) để truy cập Web Metabase.
---
## ⚙️ Cấu hình Metabase
Thông số kết nối MongoDB:

| Trường | Giá trị |
|--------|---------|
| Name | Bất động sản |
| Host | `mongodb-service` |
| Port | `27017` |
| Database name | `real_estate_db` |
| Username | _(để trống)_ |
| Password | _(để trống)_ |

## 🔌 Tích hợp với Spark Streaming

### **1. Cấu hình writeStream**

| Mục | Giá trị |
|----|---------|
| Connection URI | `mongodb://mongodb-service:27017` |
| Database | `real_estate_db` |
| Collection | `listings` |

---

### **2. Cấu trúc dữ liệu Output Schema**
| Tên cột                  | Type      | Example             | Note |
|--------------------------|-----------|----------------------|------|
| id                       | String    | "127635488"         | Id duy nhất |
| price                    | int64     | 720000000           | Giá |
| width                    | double    | 3.2                  | Rộng |
| length                   | double    | 11.8                 | Dài |
| street_name              | String    | "Phố Vĩnh Hưng"     | Tên đường |
| category_name            | String    | "Nhà ở"             | Loại (Nhà ở, Căn hộ/Chung cư, Đất). **Lưu ý:** Có loại *phòng trọ* nhưng số lượng ít → bỏ qua. |
| rooms                    | int32     | 7                    | Số phòng |
| size                     | double    | 38                   | Diện tích đất |
| living_size              | double    | 38                   | Diện tích sử dụng |
| ward                     | String    | "Phường Vĩnh Hưng"  | Phường, xã, thị trấn |
| area                     | String    | "Quận Hoàng Mai"    | Quận, huyện |
| region                   | String    | "Hà Nội"            | Tỉnh |
| is_main_street           | Boolean   | false                | Có ở mặt đường không? |
| property_legal_document  | Boolean   | true                 | Có giấy tờ pháp lý (sổ) không? |
| status                   | Boolean   | true                 | True = đang khả dụng (đang bán) |

---
## 👉 Dashboard Demo với dữ liệu giả lập
<img width="992" height="871" alt="image" src="https://github.com/user-attachments/assets/5484cb2a-6689-4420-a5f0-6da5751ce68e" />

