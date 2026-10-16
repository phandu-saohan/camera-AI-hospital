# HƯỚNG DẪN TRIỂN KHAI HỆ THỐNG — AI HOSPITAL CAMERA V1.0

## 1. Yêu Cầu Phần Cứng Máy Chủ Bệnh Viện (On-Premise Server)

### Quy mô 50–100 Camera:
- **CPU:** Intel Xeon Silver hoặc AMD EPYC 16 cores / 32 threads trở lên
- **RAM:** 64 GB DDR4/DDR5 ECC
- **GPU:** 1x NVIDIA Tesla T4 (16GB) hoặc NVIDIA RTX A4000 (16GB)
- **Ổ cứng:** 500GB NVMe SSD (Hệ điều hành + CSDL) + 4TB Enterprise HDD / SSD (Lưu trữ ảnh bằng chứng sự cố)
- **Mạng:** 2x Cổng mạng 10Gbps (1 cổng nối VLAN Camera, 1 cổng nối mạng LAN máy trạm bệnh viện)

### Quy mô 101–200 Camera:
- **GPU:** 2x NVIDIA Tesla T4 hoặc 2x NVIDIA RTX A4000
- **RAM:** 128 GB ECC

---

## 2. Các Bước Cài Đặt Trên Ubuntu Server 22.04 LTS

```bash
# 1. Cập nhật hệ thống và cài đặt Docker + NVIDIA Container Toolkit
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git make postgresql-client ffmpeg

# Cài Docker Engine & Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. Cài đặt NVIDIA Drivers & Container Toolkit (cho GPU)
sudo apt install -y nvidia-driver-535
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# 3. Clone source code và thiết lập môi trường
git clone <repository_url> /opt/ai-hospital-camera
cd /opt/ai-hospital-camera
cp .env.example .env

# Chỉnh sửa file .env với mật khẩu database và subnet camera thật
nano .env

# 4. Khởi chạy hệ thống sản xuất có GPU
docker compose -f compose.yaml -f compose.gpu.yaml up -d

# 5. Kiểm tra trạng thái dịch vụ
docker compose ps
curl http://localhost:8000/health/ready
```
