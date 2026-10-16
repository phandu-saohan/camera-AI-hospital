# GIỚI HẠN KỸ THUẬT ĐÃ GHI NHẬN — AI HOSPITAL CAMERA V1.0

## 1. Môi Trường Hiện Tại
- **Không có NVIDIA GPU vật lý trong môi trường test hiện tại:** Lệnh `nvidia-smi` không tìm thấy thiết bị. Hệ thống đã tự động suy thoái an toàn (Graceful Degradation) sang chế độ **CPU Fallback**.
- **Docker Daemon chưa khởi chạy trên môi trường sandbox:** Do đó lệnh `docker compose` cần môi trường Docker máy chủ thật để chạy trọn gói container. Môi trường phát triển cục bộ (`python -m uvicorn` và `npm run dev`) hoạt động hoàn hảo.

## 2. Giới Hạn Tính Năng AI
- **Cảnh báo té ngã (Fall Detection):** Dựa trên biến thiên tỷ lệ khung bao và chuyển động. Có thể xảy ra báo động giả khi bệnh nhân chủ động nằm nghỉ trên sàn hoặc cúi nhặt đồ vật. Bắt buộc nhân viên điều dưỡng xác nhận trực quan.
- **Phát hiện che khuất camera (Camera Tampering):** Cần điều kiện ánh sáng ổn định; nếu toàn bộ phòng bị ngắt cầu dao điện, hệ thống sẽ phát hiện mất tín hiệu/màn hình đen thay vì hành vi phá hoại cố ý.

## 3. Khuyến Cáo Khi Nâng Cấp
- Cần hoàn thành đánh giá tác động quyền riêng tư (DPIA) trước khi kết nối camera thực tế tại các khu vực chăm sóc bệnh nhân nội trú.
