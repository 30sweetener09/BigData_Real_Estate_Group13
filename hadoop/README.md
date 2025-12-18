# Hadoop Setup Guide

## Prerequisites

### Install Chocolatey
Check if Chocolatey is installed:
```powershell
choco -v
```

If not installed, run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = `
    [System.Net.ServicePointManager]::SecurityProtocol `
    -bor [System.Net.SecurityProtocolType]::Tls12; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Close and reopen PowerShell as Administrator, then verify:
```powershell
choco -v
```

## Install Helm

Install Kubernetes Helm:
```powershell
choco install kubernetes-helm -y
helm version
```

## Setup Hadoop Helm Repository

Add the Hadoop Helm repository:
```bash
helm repo add pfisterer https://pfisterer.github.io/apache-hadoop-helm/
helm repo update
```

## Configure and Install Hadoop

Create `my-hadoop-values.yaml`:
```yaml
hdfs:
  dataNode:
     externalHostname: ""
     config:
        hdfsSite:
          dfs.datanode.use.datanode.hostname: "true"
          dfs.client.use.datanode.hostname: "true"
          dfs.namenode.datanode.registration.ip-hostname-check: "false"
          dfs.replication: "1"
  nameNode:
     config:
        hdfsSite:
          dfs.client.use.datanode.hostname: "true"
          dfs.datanode.use.datanode.hostname: "true"
```

Deploy Hadoop:
```bash
helm install my-hadoop pfisterer/hadoop -f my-hadoop-values.yaml --namespace default
```

## Verify Installation

Monitor pod status:
```bash
kubectl get pods -n default -w
```

<!-- 
Chờ cho đến khi tất cả các pod có trạng thái `Running` và `READY`.
Điều này đảm bảo rằng tất cả các thành phần của Hadoop cluster đã được khởi động hoàn toàn
và sẵn sàng để xử lý công việc.
-->
Wait until all pods are `Running` and `READY` status.

```bash
kubectl get pods -n default
```

This command displays the final status of all pods without the watch flag (`-w`), allowing you to confirm the installation is complete.
