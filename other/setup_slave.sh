#!/bin/bash
set -e

echo "[1/5] Cập nhật và cài đặt các gói cơ bản..."
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl

echo "[2/5] Thêm kho Kubernetes và cài Docker..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update -y
sudo apt-get install -y docker.io kubelet kubeadm kubectl
sudo systemctl enable docker
sudo systemctl start docker

echo "[3/5] Tắt swap (Kubernetes yêu cầu)..."
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

echo "[4/5] Cấu hình sysctl cho Kubernetes..."
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sudo sysctl --system

echo "[5/5] Tham gia vào cluster (bạn cần chạy lệnh join từ master)..."
echo
echo ">>> Khi master đã khởi tạo xong, chạy lệnh 'kubeadm token create --print-join-command' trên master"
echo ">>> Sau đó copy và chạy lệnh đó tại node này."
echo
echo "Ví dụ:"
echo "    sudo kubeadm join <MASTER_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash sha256:<HASH>"
