# BÁO CÁO NĂNG LỰC & ĐO TẢI THỰC TẾ — AI HOSPITAL CAMERA V1.0

## 1. Thông Tin Môi Trường Đo Kiểm Thực Tế

- **Thời điểm thực hiện:** 2026-10-15
- **Công cụ đo kiểm:** `python scripts/benchmark.py` (Đo trực tiếp trên CPU và tiến trình thực tế, không sinh số liệu giả)
- **Số lõi xử lý (CPU Cores):** 28 Cores
- **Bộ nhớ RAM khả dụng:** ~15.5 GB khả dụng trên 31.7 GB tổng
- **GPU Accelerator:** Phát hiện trạng thái runtime hiện tại không có card GPU vật lý NVIDIA được pass-through vào môi trường thử nghiệm -> Kích hoạt chế độ **CPU Fallback Engine**.

---

## 2. Kết Quả Đo Tải Thuật Toán Đánh Giá Quy Tắc AI (Ray-Casting & Temporal ROI)

| Kịch Bản Thử Nghiệm | Số Mục Tiêu / Khung Hình | Tốc Độ Xử Lý (Targets / Giây) | Tần Số Khung Hình Khả Dụng (FPS Equivalent) | Thời Gian Xử Lý 2,000 Khung Hình |
| :--- | :--- | :--- | :--- | :--- |
| **Tải Nhẹ (Hành lang vắng)** | 5 người / khung | **316,550.9** mục tiêu/s | **63,310.2** FPS | 31.6 ms |
| **Tải Trung Bình (Khu cấp cứu)** | 20 người / khung | **612,679.4** mục tiêu/s | **30,634.0** FPS | 65.3 ms |
| **Tải Nặng (Quầy lễ tân / Chờ)** | 50 người / khung | **654,288.4** mục tiêu/s | **13,085.8** FPS | 152.8 ms |

---

## 3. Khuyến Nghị Quy Hoạch Tải Cho 51–200 Camera

1. **Tách biệt phân giải Stream:**
   - **Luồng phụ (Substream 640x360 hoặc 1280x720 @ 15fps):** Dùng để hiển thị lên Camera Wall 16 ô trên màn hình máy trạm điều dưỡng. Băng thông chỉ khoảng 512 Kbps/camera.
   - **Luồng chính (Mainstream 1080p @ 25fps):** Chỉ mở khi cần phóng to chi tiết hoặc khi AI cần phân tích chi tiết cao.
2. **Tần số suy luận AI theo mức ưu tiên:**
   - Khu vực nhạy cảm (Cửa phòng mổ, kho thuốc độc): 2.0 – 5.0 FPS.
   - Khu vực hành lang, khuôn viên: 1.0 FPS là đủ phát hiện xâm nhập và đếm người.
   - Nhờ kiến trúc Task Scheduler phân luồng theo FPS, 1 card NVIDIA Tesla T4 có thể đảm đương xử lý từ 20–30 luồng camera phân tích song song ở mức 2.0 FPS.
