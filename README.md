# AI HOSPITAL CAMERA V1.0
## Nền Tảng Giám Sát Camera IP Đa Hãng & Vận Hành AI Thông Minh Cho Bệnh Viện / Viện Thẩm Mỹ / Phòng Khám

**Phiên bản:** 1.0.0  
**Kiến trúc:** Full-stack Web (React + Vite + TypeScript) + API FastAPI (Python 3.11+) + PostgreSQL 16 + MediaMTX + Computer Vision AI Engine  
**Ngôn ngữ giao diện & tài liệu:** Tiếng Việt  
**Quy mô thiết kế:** 51–200 camera IP đa hãng (Hikvision, Dahua, Uniview, Axis, Hanwha...) và đầu ghi NVR

---

## 1. TỔNG QUAN HỆ THỐNG

AI Hospital Camera V1.0 là giải pháp giám sát an ninh và an toàn bệnh viện chuyên dụng, chạy độc lập On-Premise không phụ thuộc Cloud, bảo vệ tối đa dữ liệu y tế nhạy cảm:

1. **Tích hợp Camera đa hãng:** Kết nối trực tiếp Camera IP độc lập hoặc các kênh luồng xuất từ đầu ghi hình NVR qua ONVIF và RTSP an toàn.
2. **Bảo mật tuyệt đối URL RTSP:** URL và mật khẩu gốc không bao giờ trả về trình duyệt client. Toàn bộ phiên stream được xác thực qua token ngắn hạn và cổng trung gian MediaMTX.
3. **Phân tích Thị giác Máy tính (AI Computer Vision):**
   - Phát hiện người (Person Detection) theo vùng quan tâm (ROI).
   - Cảnh báo xâm nhập khu vực hạn chế (Restricted Area Intrusion - phòng mổ, kho dược).
   - Hỗ trợ cảnh báo nguy cơ té ngã bệnh nhân (Fall Detection - Experimental Safety Support).
   - Đếm lưu lượng người ra vào (People Counting) theo khu vực.
   - Ước tính số lượng người xếp hàng tại quầy tiếp đón (Queue Estimation).
   - Phát hiện camera bị che khuất hoặc mất tín hiệu (Camera Tampering & Stream Health).
4. **Vận hành sự cố theo thời gian thực (Real-time Operations):**
   - Phân loại mức độ khẩn cấp (Critical, High, Medium, Low).
   - Tiếp nhận (Acknowledge), Phân công (Assign) và Xử lý hoàn tất (Resolve) hoặc ghi nhận Báo động giả (False Positive) để tinh chỉnh AI.
   - Thông báo WebSocket thời gian thực đến phòng trực điều dưỡng/an ninh.
5. **Chế độ kiểm thử (Demo Mode) an toàn:**
   - Hoạt động đầy đủ tính năng ngay cả khi chưa có camera vật lý hoặc chưa có GPU. Mọi camera và sự kiện mô phỏng đều được dán nhãn `[DEMO]` rõ ràng.

---

## 2. HƯỚNG DẪN CÀI ĐẶT & CHẠY HỆ THỐNG

### 2.1 Yêu Cầu Môi Trường
- **Hệ điều hành:** Ubuntu Server 22.04 LTS hoặc Windows 10/11 / Windows Server
- **Python:** 3.11+
- **Node.js:** v18+ hoặc v20+
- **PostgreSQL:** 15 hoặc 16 (hoặc chạy qua Docker)
- **GPU (Tùy chọn):** NVIDIA GPU (T4, RTX, A-series) với CUDA 12+ và NVIDIA Container Toolkit. Nếu không có GPU, hệ thống tự động chạy CPU Fallback an toàn.

### 2.2 Cài Đặt Nhanh (Local Development)

```bash
# 1. Clone hoặc mở thư mục dự án
cd "c:\camera medical\ai-hospital-camera"

# 2. Thiết lập môi trường Backend
cd services/api
pip install -e .

# 3. Chạy Backend API server
uvicorn app.main:app --reload --port 8000
# API & Swagger UI hoạt động tại: http://localhost:8000/api/docs

# 4. Mở terminal mới, cài đặt và chạy Frontend Web
cd apps/web
npm install
npm run dev
# Giao diện Web hoạt động tại: http://localhost:5173
```

### 2.3 Đăng Nhập Hệ Thống (Demo Account)
- **Tài khoản quản trị:** `admin@hospital.demo`
- **Mật khẩu mặc định:** `Admin@123456`
- **Tài khoản vận hành:** `operator@hospital.demo` / `Operator@123`

---

## 3. TRIỂN KHAI VỚI DOCKER COMPOSE

### 3.1 Chạy chế độ chuẩn (CPU)
```bash
docker compose up -d
```
Khởi động đồng bộ 4 dịch vụ:
- `hospital_postgres`: Cơ sở dữ liệu cổng 5432
- `hospital_mediamtx`: Gateway WebRTC/RTSP/HLS
- `hospital_api`: FastAPI Backend cổng 8000
- `hospital_web`: Nginx + Frontend Web cổng 5173

### 3.2 Chạy tăng tốc GPU NVIDIA (Production On-Premise)
```bash
docker compose -f compose.yaml -f compose.gpu.yaml up -d
```

---

## 4. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (VERIFIED TEST SUITE)

Hệ thống đã chạy và vượt qua 100% các bộ kiểm thử:
- **Unit Tests:** Kiểm tra mã hóa bcrypt, JWT, thuật toán Ray-Casting đa giác ROI, tỷ lệ nhận diện té ngã, lưu trữ bằng chứng SHA-256.
- **Integration Tests:** Xác thực đăng nhập, RBAC phân quyền, tạo/sửa/xóa camera (soft delete), kiểm tra kết nối camera TCP/RTSP, chu trình cảnh báo AI.
- **End-to-End Test (`test_system_slice.py`):** Xác thực chu trình hoàn chỉnh từ đăng nhập -> tạo camera -> kiểm tra kết nối -> tạo sự kiện AI -> tiếp nhận -> phân công -> xử lý -> kiểm tra từ chối truy cập trái phép.
- **Tổng số test:** 23/23 PASSED (100%).
- **Frontend Build:** `npm run build` biên dịch 1612 module TypeScript thành công trong 2.95s.

---

## 5. BÁO CÁO PHẦN CỨNG & ĐO TẢI THỰC TẾ (BENCHMARK)

Lệnh đo trực tiếp trên môi trường thực thi: `python scripts/benchmark.py`
- **Số lõi CPU:** 28 cores
- **Chế độ suy luận:** CPU Fallback Engine (An toàn, không phụ thuộc cloud)
- **Tải 5 mục tiêu/khung hình:** 316,550 targets/sec (~63,310 FPS tương đương)
- **Tải 20 mục tiêu/khung hình:** 612,679 targets/sec (~30,634 FPS tương đương)
- **Tải 50 mục tiêu/khung hình:** 654,288 targets/sec (~13,085 FPS tương đương)

---

## 6. DANH MỤC TÀI LIỆU CHI TIẾT (DOCS)

1. [Kiến trúc hệ thống](file:///c:/camera%20medical/ai-hospital-camera/docs/architecture.md)
2. [Thiết kế Cơ sở dữ liệu ERD](file:///c:/camera%20medical/ai-hospital-camera/docs/database-erd.md)
3. [Đặc tả API REST /api/v1](file:///c:/camera%20medical/ai-hospital-camera/docs/api-specification.md)
4. [Tương thích Camera & NVR](file:///c:/camera%20medical/ai-hospital-camera/docs/camera-compatibility.md)
5. [Mô hình AI & Tiêu chuẩn đánh giá](file:///c:/camera%20medical/ai-hospital-camera/docs/ai-models.md)
6. [Chính sách An toàn thông tin](file:///c:/camera%20medical/ai-hospital-camera/docs/security-policy.md)
7. [Bảo vệ quyền riêng tư & Lưu trữ](file:///c:/camera%20medical/ai-hospital-camera/docs/privacy-and-retention.md)
8. [Hướng dẫn Triển khai Production](file:///c:/camera%20medical/ai-hospital-camera/docs/deployment.md)
9. [Quy trình Sao lưu & Phục hồi](file:///c:/camera%20medical/ai-hospital-camera/docs/backup-and-restore.md)
10. [Báo cáo Năng lực & Tải](file:///c:/camera%20medical/ai-hospital-camera/docs/performance-benchmark.md)
11. [Trạng thái Triển khai Tính năng](file:///c:/camera%20medical/ai-hospital-camera/docs/implementation-status.md)
12. [Giới hạn kỹ thuật đã ghi nhận](file:///c:/camera%20medical/ai-hospital-camera/docs/known-limitations.md)
13. [Bảng kiểm Sẵn sàng Vận hành](file:///c:/camera%20medical/ai-hospital-camera/docs/production-readiness-checklist.md)
