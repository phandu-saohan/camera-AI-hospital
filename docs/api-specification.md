# ĐẶC TẢ API RESTFUL — AI HOSPITAL CAMERA V1.0

Tiền tố chung: `/api/v1`  
Tài liệu tương tác trực tiếp (Swagger UI): `http://localhost:8000/api/docs`

---

## 1. Xác thực & Quản lý Phiên (Authentication)

| Phương thức | Đường dẫn | Phân quyền | Mô tả chức năng |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Public | Đăng nhập bằng email/password, trả về Access/Refresh Token |
| `POST` | `/auth/refresh` | Bearer Refresh | Cấp lại access token mới |
| `POST` | `/auth/logout` | Bearer Access | Đăng xuất và ghi nhận nhật ký audit |
| `GET` | `/auth/me` | Bearer Access | Lấy thông tin tài khoản đang đăng nhập |

## 2. Quản lý Danh mục Camera (Cameras)

| Phương thức | Đường dẫn | Phân quyền | Mô tả chức năng |
| :--- | :--- | :--- | :--- |
| `GET` | `/cameras` | `cameras:read` | Lấy danh sách camera (phân trang, lọc theo vị trí, status) |
| `POST` | `/cameras` | `cameras:write` | Thêm camera mới (chấp nhận RTSP URL mã hóa bảo mật) |
| `GET` | `/cameras/{id}` | `cameras:read` | Lấy chi tiết camera (không trả về mật khẩu gốc) |
| `PATCH` | `/cameras/{id}` | `cameras:write` | Cập nhật cấu hình camera |
| `DELETE` | `/cameras/{id}` | `cameras:admin` | Xóa mềm camera (Soft Delete bảo toàn dữ liệu audit) |
| `POST` | `/cameras/{id}/test-connection` | `cameras:read` | Kiểm tra kết nối TCP/RTSP thực tế và ghi health log |
| `GET` | `/cameras/health` | `cameras:read` | Lấy tóm tắt trạng thái online/offline toàn bộ camera |
| `GET` | `/cameras/{id}/health-history` | `cameras:read` | Xem lịch sử đo độ trễ và sự cố mất tín hiệu |

## 3. Cảnh báo & Vận hành Sự cố (Events & Alerts)

| Phương thức | Đường dẫn | Phân quyền | Mô tả chức năng |
| :--- | :--- | :--- | :--- |
| `GET` | `/events` | `events:read` | Danh sách sự kiện AI (phân trang, lọc theo độ nghiêm trọng) |
| `GET` | `/events/{id}` | `events:read` | Xem chi tiết sự kiện và metadata phát hiện |
| `POST` | `/events/{id}/acknowledge` | `events:write` | Nhân viên trực bấm tiếp nhận cảnh báo |
| `POST` | `/events/{id}/assign` | `events:write` | Phân công sự cố cho nhân viên xử lý |
| `POST` | `/events/{id}/resolve` | `events:write` | Đóng sự cố hoặc đánh dấu Báo động giả (False Positive) |
| `GET` | `/events/{id}/evidence` | `events:read` | Lấy link tải bằng chứng tạm thời có hạn 15 phút |

## 4. Kiểm tra Sức khỏe Dịch vụ (Health Probes)

| Phương thức | Đường dẫn | Mô tả |
| :--- | :--- | :--- |
| `GET` | `/health/live` | Kubernetes / Docker Liveness probe (tiến trình đang chạy) |
| `GET` | `/health/ready` | Readiness probe (kiểm tra kết nối PostgreSQL và AI engine) |
| `GET` | `/metrics` | Chỉ số vận hành camera online/offline và tổng sự cố |
