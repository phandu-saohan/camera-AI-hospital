# BẢNG KIỂM SẴN SÀNG VẬN HÀNH (PRODUCTION READINESS CHECKLIST)

Bảng kiểm tra bắt buộc trước khi đưa hệ thống AI Hospital Camera vào kết nối với camera thật tại bệnh viện:

| Hạng Mục | Yêu Cầu Kỹ Thuật | Trạng Thái | Ghi Chú |
| :--- | :--- | :---: | :--- |
| **Bảo Mật Mật Khẩu** | Đổi toàn bộ SECRET_KEY và mật khẩu mặc định của admin trong file `.env` | ⚠️ BẮT BUỘC | Không dùng mật khẩu mẫu demo |
| **Phân Tách Mạng (VLAN)** | Đặt camera IP và NVR vào một VLAN riêng biệt, không nối Internet | ⚠️ BẮT BUỘC | Ngăn chặn camera bị tấn công botnet |
| **Cấu Hình Subnet Cho Phép** | Cập nhật `CAMERA_ALLOWED_SUBNETS` chính xác theo dải IP camera nội bộ | ⚠️ BẮT BUỘC | Ngăn chặn lỗ hổng SSRF |
| **Chứng Chỉ SSL/HTTPS** | Cài đặt chứng chỉ SSL/TLS hợp lệ cho domain máy chủ Web và API | ⚠️ BẮT BUỘC | Bảo vệ luồng WebRTC và token đăng nhập |
| **Kiểm Thử Tải GPU** | Chạy benchmark trên card NVIDIA GPU thật với 5 -> 20 -> 50 camera đồng thời | ⚠️ BẮT BUỘC | Điều chỉnh FPS suy luận phù hợp |
| **Quy Trình Sao Lưu** | Cấu hình cronjob tự động chạy `scripts/backup_db.py` lên ổ cứng sao lưu | ⚠️ BẮT BUỘC | Kiểm tra định kỳ khả năng restore |
| **Phê Duyệt Pháp Lý** | Ban hành nội quy thông báo có camera giám sát an ninh tại bệnh viện | ⚠️ BẮT BUỘC | Tuân thủ Nghị định 13/2023/NĐ-CP |
