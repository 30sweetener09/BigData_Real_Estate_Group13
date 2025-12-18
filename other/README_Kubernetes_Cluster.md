# Hướng dẫn cài đặt cụm Kubernetes (VMware + kubeadm + Flannel)


## 1. Cấu trúc cụm

| Node | Vai trò | Tên máy (hostname) ví dụ | Địa chỉ IP ví dụ |
|------|----------|--------------------------|------------------|
| Master | Control Plane | vanserver | 192.168.1.110 |
| Worker 1 | Worker Node | worker1 | 192.168.1.111 |
| Worker 2 | Worker Node | worker2 | 192.168.1.112 |

Tất cả máy đều chạy **Ubuntu 20.04 LTS** (hoặc mới hơn).

## 2. Yêu cầu trước khi cài đặt

1. Mỗi máy ảo cần có:
   - Ít nhất **2 CPU**, **2 GB RAM**, **20 GB ổ đĩa**
   - Đặt **IP tĩnh** và **ping được lẫn nhau**
2. Có kết nối Internet để tải các gói cài đặt
3. Tắt swap trên tất cả các node:
   ```bash
   sudo swapoff -a
   sudo sed -i '/ swap / s/^/#/' /etc/fstab
   ```
4. Đảm bảo đồng bộ thời gian giữa các máy (có thể dùng `chrony` hoặc `ntp`).

## 3. Các bước cài đặt

### Bước 1. Clone repository
Thực hiện trên **tất cả các node**:
```bash

chmod +x setup_master.sh setup_slave.sh
```

### Bước 2. Cài đặt Master Node
Trên **máy master** (ví dụ: `vanserver`):
```bash
sudo ./setup_master.sh
```

Script này sẽ:
- Cài **containerd**
- Cài **kubeadm**, **kubelet**, **kubectl**
- Khởi tạo cụm Kubernetes
- Cấu hình `kubectl` cho người dùng hiện tại
- Cài **Flannel CNI** để kết nối mạng giữa các node

Cuối quá trình, script sẽ in ra lệnh `kubeadm join`. Hãy **copy lại lệnh này** để dùng ở bước tiếp theo.

### Bước 3. Cài đặt Worker Nodes
Trên **mỗi máy worker**:
```bash
sudo ./setup_slave.sh
```

Sau đó, **chạy lệnh `kubeadm join`** mà bạn đã copy ở bước 2.  
Ví dụ:
```bash
sudo kubeadm join 192.168.1.110:6443 --token <token>     --discovery-token-ca-cert-hash sha256:<hash>
```

Sau vài phút, node worker sẽ tự động tham gia cụm.

### Bước 4. Kiểm tra cụm

Trên **máy master**:
```bash
kubectl get nodes -o wide
```

Kết quả mong đợi:
```
NAME        STATUS   ROLES           AGE   VERSION
vanserver   Ready    control-plane   XXm   v1.31.x
worker1     Ready    worker          XXm   v1.31.x
worker2     Ready    worker          XXm   v1.31.x
```

Kiểm tra pod của Flannel:
```bash
kubectl get pods -n kube-flannel -o wide
```
Tất cả phải ở trạng thái `Running`.

## 5. Khắc phục sự cố

| Lỗi | Nguyên nhân | Cách khắc phục |
|------|--------------|----------------|
| Worker hiển thị `NotReady` | Flannel CNI chưa được cài | Chạy lại lệnh: `kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml` |
| Lỗi `connection refused on localhost:8080` | Thiếu file kubeconfig | Chạy: `mkdir -p $HOME/.kube && sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config` |
| Pod bị kẹt ở `ContainerCreating` | Mạng CNI chưa được thiết lập | Kiểm tra `/etc/cni/net.d/10-flannel.conflist` và `/run/flannel/subnet.env` có tồn tại không |

## 6. Bước tiếp theo


**Môn học:** Lưu trữ và xử lý dữ liệu lớn  
