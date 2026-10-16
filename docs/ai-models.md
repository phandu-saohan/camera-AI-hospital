# MÔ HÌNH AI & TIÊU CHUẨN ĐÁNH GIÁ — AI HOSPITAL CAMERA V1.0

## 1. Danh Mục Các Tác Vụ Computer Vision Trong Bệnh Viện

### 1.1 Phát Hiện Người (Person Detection)
- **Kiến trúc mô hình:** YOLOv8n / YOLOv8s tối ưu hóa TensorRT FP16 hoặc CPU INT8.
- **Tiêu chuẩn:** Nhận diện người với ngưỡng tin cậy (Confidence Threshold) có thể cấu hình từ 0.35 đến 0.85.
- **Quyền riêng tư:** Không lưu trữ và không sử dụng tính năng nhận diện khuôn mặt (Face Recognition) trong phiên bản V1.0.

### 1.2 Xâm Nhập Khu Vực Hạn Chế (Restricted Area Monitoring)
- **Cơ chế:** Kết hợp nhận diện người và thuật toán kiểm tra điểm nằm trong đa giác Ray-Casting.
- **Lịch trình:** Hỗ trợ cấu hình theo ca trực (ví dụ chỉ kích hoạt từ 22:00 đến 06:00 sáng tại hành lang phẫu thuật).
- **Chống báo động lặp (Cooldown):** Tự động bỏ qua các sự kiện trùng lặp trong khoảng thời gian cấu hình (mặc định 60 giây).

### 1.3 Cảnh Báo Té Ngã (Fall Detection - Experimental Safety Support)
- **Phân loại tính năng:** Đây là tính năng hỗ trợ an toàn thử nghiệm (Safety-Support Feature), không thay thế thiết bị y tế chẩn đoán lâm sàng.
- **Phương pháp kỹ thuật:** Theo dõi sự thay đổi đột ngột về tỷ lệ khung bao (Aspect Ratio Height/Width chuyển từ đứng >1.8 sang nằm <0.8) và dịch chuyển trọng tâm nhanh theo phương thẳng đứng.
- **Quy trình:** Bắt buộc có nhân viên điều dưỡng xác nhận trực quan trước khi đưa ra hành động hỗ trợ y tế.

### 1.4 Đếm Người & Ước Tính Hàng Đợi (Counting & Queue Estimation)
- Theo dõi chuyển động người qua vạch ảo phân định cửa ra vào.
- Ước tính số lượng người đang chờ tại vùng đa giác quầy đăng ký khám bệnh.

### 1.5 Phát Hiện Che Khuất / Phá Hoại Camera (Camera Tampering)
- Phát hiện tình trạng mất tín hiệu luồng RTSP đột ngột.
- Phát hiện khung hình bị đen hoàn toàn, hình bị đóng băng (frozen) hoặc mất toàn bộ biên cạnh (edge loss) do camera bị xịt sơn hoặc che ống kính.
