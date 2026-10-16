# QUYỀN RIÊNG TƯ & CHÍNH SÁCH LƯU TRỮ — AI HOSPITAL CAMERA V1.0

## 1. Tuân Thủ Pháp Luật Việt Nam Về Bảo Vệ Dữ Liệu Cá Nhân

- **Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân:**
  - Hình ảnh bệnh nhân và người thăm bệnh là dữ liệu cá nhân. Hệ thống được thiết kế chạy On-Premise hoàn toàn trong mạng nội bộ bệnh viện, không gửi video ra bất kỳ dịch vụ Cloud AI bên thứ ba nào.
  - V1.0 tắt hoàn toàn tính năng nhận diện danh tính và khuôn mặt.
  - Hỗ trợ làm mờ (Privacy Masking) tại các khu vực nhạy cảm (giường bệnh, buồng khám riêng tư).

## 2. Chính Sách Lưu Trữ Bằng Chứng & Video (Retention Policy)

| Loại Dữ Liệu | Thời Gian Lưu Trữ Khuyến Nghị | Cơ Chế Thu Gom / Xóa |
| :--- | :--- | :--- |
| **Ảnh chụp bằng chứng (Snapshot)** | 30 ngày | Retention Worker xóa tự động hàng ngày |
| **Video clip sự cố (5-15 giây)** | 14 ngày | Retention Worker xóa tự động khi hết hạn |
| **Luồng ghi liên tục 24/7** | 30–90 ngày | Giữ nguyên tại đầu ghi NVR chuyên dụng, không trùng lặp |
| **Nhật ký sự kiện & Audit log** | 365 ngày (1 năm) | Lưu trữ vĩnh viễn trong CSDL để phục vụ kiểm toán |

## 3. Xác Thực Tính Toàn Vẹn Bằng Chứng
- Mỗi file snapshot khi ghi nhận đều được tính toán mã băm SHA-256 lưu trong bảng `event_evidence`.
- Khi xuất file phục vụ điều tra an ninh, hệ thống đối soát mã SHA-256 để đảm bảo hình ảnh không bị can thiệp chỉnh sửa.
