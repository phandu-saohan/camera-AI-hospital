# CHÍNH SÁCH AN TOÀN THÔNG TIN & BẢO MẬT — AI HOSPITAL CAMERA V1.0

## 1. Nguyên Tắc An Toàn Dữ Liệu Video Y Tế

1. **Không mở luồng RTSP trực tiếp ra ngoài Internet:**
   - Tuyệt đối không NAT cổng RTSP 554 ra môi trường công cộng.
   - Trình duyệt chỉ được xem video qua WebRTC / HLS từ MediaMTX sau khi được FastAPI xác thực token phiên ngắn hạn.
2. **Không để lộ thông tin xác thực Camera (Credential Sanitization):**
   - Tên đăng nhập và mật khẩu camera được mã hóa khi lưu trữ trong cơ sở dữ liệu.
   - Response của API, nhật ký log và state trình duyệt tuyệt đối không chứa mật khẩu hay URL thô `rtsp://user:pass@host`.
3. **Phân quyền dựa trên vai trò nghiêm ngặt (RBAC):**
   - `Administrator`: Toàn quyền cấu hình camera, tài khoản, hệ thống.
   - `Operator`: Quản lý camera, quy tắc AI, tiếp nhận và xử lý sự cố.
   - `Viewer`: Chỉ xem video và theo dõi cảnh báo thuộc khoa phòng được phân công.
4. **Bảo vệ chống SSRF (Server-Side Request Forgery):**
   - Chỉ cho phép kiểm tra kết nối tới các IP nằm trong danh sách subnet được cấu hình sẵn trong `CAMERA_ALLOWED_SUBNETS`.
5. **Nhật ký Kiểm toán Toàn diện (Audit Trail):**
   - Mọi hành động đăng nhập, thay đổi cấu hình camera, xuất bằng chứng, đóng sự cố đều được ghi log vào bảng `audit_logs` kèm địa chỉ IP và định danh người dùng.
