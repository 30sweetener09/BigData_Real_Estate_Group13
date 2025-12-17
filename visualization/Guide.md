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
py test_dashboard.py clean
```

#### Terminal B: Dùng để truy cập Web Metabase
Gõ lệnh:
```bash
minikube service metabase-service
```
Nó sẽ tự bật 1 trình duyệt với địa chỉ 127.0.0.1:xxxx với cổng ngẫu nhiên để truy cập Web Metabase

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
| latitude                 | double    |                     | Vĩ độ |
| longitude                | double    |                     | Kinh độ |
| is_main_street           | Boolean   | false                | Có ở mặt đường không? |
| property_legal_document  | Boolean   | true                 | Có giấy tờ pháp lý (sổ) không? |
| status                   | Boolean   | true                 | True = đang khả dụng (đang bán) |

---
## Tổng hợp các câu truy vấn (Native Queries) cho dữ liệu 
#### 1. Dashboard KPI tổng quan
Các chỉ số người dùng có thể quan tâm:
- Tổng tin đang bán
- Giá trung bình (VND)
- Diện tích trung bình (m²)
- Số quận có dữ liệu
```
[
  { $match: { status: true } },
  {
    $group: {
      _id: null,
      total_listings: { $sum: 1 },
      avg_price: { $avg: "$price" },
      avg_living_size: { $avg: "$living_size" },
      districts: { $addToSet: "$area" }
    }
  },
  {
    $project: {
      total_listings: 1,
      avg_price: { $round: ["$avg_price", 0] },
      avg_living_size: { $round: ["$avg_living_size", 2] },
      total_districts: { $size: "$districts" }
    }
  }
]
```
Có thể thêm timestamp để xác định Trend theo thời gian
#### 2. Phân bố tin đăng theo khu vực (Độ sôi động thị trường)
- Xác định độ sôi động thị trường, nơi nào nhiều nguồn cung để xác định giá cả và xu hướng.
- Biểu đồ: Bar hoặc Pie Chart
```
[
  { $match: { status: true } },
  {
    $group: {
      _id: "$area",
      total_listings: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: null,
      district: "$_id",
      total_listings: 1
    }
  },
  { $sort: { total_listings: -1 } }
]
```
#### 3. Giá nhà trung bình theo khu vực
- So sánh mức giá trung bình giữa các quận/huyện để xác định khu vực đắt / rẻ, xu hướng thị trường.
- Biểu đồ: Bar chart (với Trục X: Quận/Huyện và trục Y: Giá trung bình)
```
[
  { $match: { status: true, price: { $gt: 0 } } },
  {
    $group: {
      _id: "$area",
      total_listings: { $sum: 1 },
      avg_price: { $avg: "$price" }
    }
  },
  {
    $project: {
      _id: null,
      district: "$_id",
      total_listings: 1,
      avg_price: { $round: ["$avg_price", 0] }
    }
  },
  { $sort: { avg_price: -1 } }
]
```
#### 4. Tỷ lệ và giá trung bình loại hình Bất Động Sản
- So sánh tỷ lệ và giá cả đối với các loại hình để xác định phân khúc phù hợp, so sánh đầu tư hiệu quả.
- Biểu đồ: Bar chart hoặc Pie chart (để so sánh tỷ trọng)
```
[
  { $match: { status: true, price: { $gt: 0 } } },
  {
    $group: {
      _id: "$category_name",
      total_listings: { $sum: 1 },
      avg_price: { $avg: "$price" }
    }
  },
  {
    $project: {
      _id: null,
      category: "$_id",
      total_listings: 1,
      avg_price: { $round: ["$avg_price", 0] }
    }
  }
]
```
#### 5. Top 10 tuyến đường "Đắt đỏ" nhất
Query đưa ra top 10 con đường có giá cao nhất (Lọc với trên 3 số lượng tin đăng và giá < 50 tỷ)
Biểu đồ: Pin map (với vĩ độ và kinh độ lấy từ dữ liệu) 
```
[
  {
    "$match": { 
      "street_name": { "$ne": "", "$exists": true },
      "price": { "$gt": 0, "$lt": 50000000000 }, 
      "latitude": { "$ne": 0 }, "longitude": { "$ne": 0 }
    }
  },
  {
    "$group": {
      "_id": "$street_name",
      "Gia_TB": { "$avg": "$price" },
      "latitude": { "$avg": "$latitude" }, 
      "longitude": { "$avg": "$longitude" },
      "So_Luong_Tin": { "$sum": 1 }
    }
  },
  { "$match": { "So_Luong_Tin": { "$gt": 3 } } },
  { "$sort": { "Gia_TB": -1 } },
  { "$limit": 10 }
]
```
Ảnh minh họa:
<img width="1320" height="717" alt="image" src="https://github.com/user-attachments/assets/8ad6b805-cb4a-4668-b19c-563a38dc5f7d" />
#### 6. Giá trị thương mại: Mặt phố và Trong ngõ

```
[
  {
    "$match": { "price": { "$gt": 0 } }
  },
  {
    "$group": {
      "_id": "$is_main_street",
      "Gia_TB": { "$avg": "$price" },
      "So_Luong": { "$sum": 1 }
    }
  }
]
```
#### 7. Xu hướng tin đăng theo thời gian
Biểu đồ: Line or Area Chart

---
## 📊 Dashboard Demo với dữ liệu giả lập
<img width="992" height="871" alt="image" src="https://github.com/user-attachments/assets/5484cb2a-6689-4420-a5f0-6da5751ce68e" />

