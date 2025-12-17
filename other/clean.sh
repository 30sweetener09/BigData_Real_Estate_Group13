# 1. Reset lại cấu hình kubeadm cũ


sudo kubeadm reset -f

# 2. Xóa dữ liệu Kubernetes cũ
sudo rm -rf /etc/kubernetes/pki
sudo rm -rf /var/lib/kubelet/*
sudo rm -rf /etc/cni/net.d
sudo rm -rf /var/lib/cni/

# 3. Restart lại dịch vụ container
sudo systemctl restart docker
sudo systemctl restart kubelet

sudo kubeadm join 192.168.1.110:6443 --token ddk97w.cune0hi907hdcd3d --discovery-token-ca-cert-hash sha256:538251199be35824f1192ca070e7baf7753d50c76e9804568db7224f69c7165b
