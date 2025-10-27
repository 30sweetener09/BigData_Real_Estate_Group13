#!/bin/bash
# ===============================================
# Kubernetes Master Setup Script (Fixed Version)
# ===============================================

set -e

echo "[1/6] Update hệ thống..."
sudo apt update && sudo apt upgrade -y

echo "[2/6] Tắt swap và cấu hình sysctl..."
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/kubernetes.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

sudo sysctl --system

echo "[3/6] Cài containerd..."
sudo apt install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd

echo "[4/6] Cài kubeadm, kubelet, kubectl (sửa lỗi GPG key)..."
sudo apt install -y apt-transport-https ca-certificates curl gpg

# Xóa repo cũ (nếu có)
sudo rm -f /usr/share/keyrings/kubernetes-archive-keyring.gpg
sudo rm -f /etc/apt/sources.list.d/kubernetes.list

# Tải key và tạo repo an toàn
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | \
sudo gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] \
https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" | \
sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

echo "[5/6] Khởi tạo Kubernetes master..."
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 | tee kubeadm-init.log

echo "[6/6] Cấu hình kubectl cho user hiện tại..."
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo "[Hoàn tất] Cài plugin mạng Flannel..."
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

echo
echo "===== THÀNH CÔNG ====="
echo "Cluster master đã sẵn sàng!"
echo "Copy lệnh 'kubeadm join' từ file kubeadm-init.log để thêm worker node."
