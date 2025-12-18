# Hướng dẫn cài đặt Minikube

## Bước 1: Tải Minikube
Tải Minikube từ trang chính thức và cài đặt.

## Bước 2: Cài đặt VirtualBox
Tải VirtualBox từ [Oracle VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads) và cài đặt.

## Bước 3: Khởi động Minikube
Mở PowerShell và chạy lệnh sau để khởi động Minikube với cấu hình tối ưu:
```bash
minikube start --driver=virtualbox --cpus 4 --memory 8192MB --disk-size 20GB
```
*Nên cài cấu hình ít nhất như trên để tránh thiếu tài nguyên.*

## Bước 4: Kiểm tra trạng thái
Sau khi cài đặt xong, bạn có thể kiểm tra trạng thái của Minikube bằng lệnh:
```bash
minikube kubectl -- get nodes
```

