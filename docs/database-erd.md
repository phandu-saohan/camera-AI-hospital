# THIẾT KẾ CƠ SỞ DỮ LIỆU (ERD) — AI HOSPITAL CAMERA V1.0

## 1. Sơ đồ Quan hệ Thực thể (ERD)

```mermaid
erDiagram
    DEPARTMENTS ||--o{ LOCATIONS : "chứa"
    LOCATIONS ||--o{ CAMERAS : "đặt tại"
    RECORDERS ||--o{ CAMERAS : "quản lý kênh"
    CAMERAS ||--o{ CAMERA_STREAMS : "có"
    CAMERAS ||--o{ CAMERA_CREDENTIALS : "lưu thông tin xác thực"
    CAMERAS ||--o{ CAMERA_HEALTH_LOGS : "lịch sử kiểm tra"
    CAMERAS ||--o{ AI_RULES : "áp dụng"
    AI_MODELS ||--o{ AI_RULES : "sử dụng"
    CAMERAS ||--o{ AI_EVENTS : "phát sinh"
    AI_RULES ||--o{ AI_EVENTS : "kích hoạt"
    AI_EVENTS ||--o{ EVENT_EVIDENCE : "chứa bằng chứng"
    AI_EVENTS ||--o{ EVENT_ASSIGNMENTS : "được phân công"
    AI_EVENTS ||--o{ EVENT_AUDIT_LOGS : "nhật ký xử lý"
    USERS ||--o{ USER_ROLES : "gán vai trò"
    ROLES ||--o{ USER_ROLES : "thuộc về"
    ROLES ||--o{ ROLE_PERMISSIONS : "sở hữu quyền"
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : "thuộc vai trò"
    USERS ||--o{ AUDIT_LOGS : "thực hiện"
```

## 2. Bảng Danh mục Thực thể Chính

| Tên Bảng | Khóa Chính | Mục Đích Lưu Trữ | Lưu Ý Bảo Mật / Chỉ Mục |
| :--- | :--- | :--- | :--- |
| `users` | UUID | Danh sách nhân viên, tài khoản đăng nhập | `email` index, mật khẩu mã hóa bcrypt |
| `roles` & `permissions` | UUID | Kiểm soát phân quyền dựa trên vai trò (RBAC) | Quyền chi tiết theo tài nguyên:action |
| `departments` & `locations` | UUID | Phân cấp vị trí thực tế trong bệnh viện | Khoa phòng, tòa nhà, tầng, số phòng |
| `recorders` | UUID | Đầu ghi hình NVR / VMS | Quản lý địa chỉ IP, hãng, model |
| `cameras` | UUID | Danh mục thiết bị camera IP | Chỉ mục `status`, cờ `is_demo`, cờ `deleted_at` |
| `camera_streams` | UUID | Luồng stream main / sub | `rtsp_url_encrypted` mã hóa server-side |
| `camera_credentials` | UUID | Mật khẩu & tài khoản camera | Mã hóa an toàn, không bao giờ gửi ra client |
| `camera_health_logs` | UUID | Lịch sử đo độ trễ và mất kết nối | Chỉ mục kép `(camera_id, checked_at)` |
| `ai_models` | UUID | Danh mục model YOLO / Pose / Action | Ghi nhận backend (cpu / cuda / tensorrt) |
| `ai_rules` | UUID | Cấu hình quy tắc AI từng camera | JSONB đa giác ROI, lịch trình, cooldown |
| `ai_events` | UUID | Sự cố và cảnh báo phát sinh từ AI | Chỉ mục `(occurred_at, status)`, `is_simulated` |
| `event_evidence` | UUID | Metadata bằng chứng (ảnh snapshot / clip) | Khóa lưu trữ relative, checksum SHA-256 |
| `audit_logs` | UUID | Nhật ký bảo mật toàn hệ thống | Ghi nhận IP, hành động, tài nguyên |
