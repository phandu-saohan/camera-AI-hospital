# BÁO CÁO TRẠNG THÁI TRIỂN KHAI TÍNH NĂNG — AI HOSPITAL CAMERA V1.0

Báo cáo phân định trung thực theo quy định nghiệm thu:

## 1. Đã Triển Khai & Kiểm Thử Thành Công (Implemented & Tested)
- [x] **Xác thực & Bảo mật:** Đăng nhập JWT, cấp lại Refresh Token, mã hóa mật khẩu bằng `bcrypt`, bảo vệ chống lộ URL RTSP thô.
- [x] **Phân quyền RBAC:** Bộ bảo vệ quyền `require_permission` theo tài nguyên và hành động (`cameras:read`, `cameras:write`, `cameras:admin`, `events:write`).
- [x] **Quản lý Camera:** CRUD danh mục camera, kênh NVR, phân cấp khoa phòng và tòa nhà, phân trang và tìm kiếm.
- [x] **Kiểm tra kết nối Camera:** Thăm dò cổng RTSP/TCP, đo độ trễ, lưu nhật ký sức khỏe `CameraHealthLog`, phát hiện camera offline.
- [x] **Xóa mềm (Soft Delete):** Xóa camera bảo toàn liên kết với các sự kiện và nhật ký kiểm toán trong quá khứ.
- [x] **Hệ thống Cảnh báo & Vận hành Sự cố:** Chu trình Tiếp nhận (`acknowledge`), Phân công (`assign`), Đóng sự cố (`resolve`), gắn cờ Báo động giả (`is_false_positive`).
- [x] **Bằng chứng số:** Lưu trữ snapshot bằng chứng với mã băm SHA-256, sinh URL truy cập tạm thời có hạn 15 phút.
- [x] **Bộ quy tắc AI:** Thuật toán Ray-Casting đa giác ROI, lọc độ tin cậy, phân loại tỷ lệ khung hình phát hiện té ngã, chống báo động lặp Cooldown.
- [x] **WebSocket Thời gian thực:** Quản lý kết nối xác thực và phát thông báo sự kiện tức thời.
- [x] **Frontend Web hoàn chỉnh:** React 18, Vite, TypeScript biên dịch thành công, hỗ trợ Dashboard, Camera Wall, Quản lý camera, Cảnh báo, Báo cáo, Phân quyền.
- [x] **Mô phỏng an toàn (Demo Mode):** Cho phép khởi chạy và thao tác đầy đủ quy trình ngay cả khi chưa có camera vật lý.

## 2. Đã Triển Khai Nhưng Chưa Thử Nghiệm Trên Phần Cứng Thật (Implemented, Hardware-Pending)
- [ ] **Tăng tốc TensorRT FP16 / DeepStream trên 2x NVIDIA T4:** Đã xây dựng cấu hình `compose.gpu.yaml` và phát hiện thiết bị tự động; cần máy chủ vật lý trang bị GPU NVIDIA để benchmark trực tiếp.
- [ ] **Stream trực tiếp từ NVR vật lý:** Đã có adapter RTSP/ONVIF và MediaMTX proxy; cần cắm vào mạng camera LAN bệnh viện thật để xác nhận stream video mượt mà.

## 3. Tính Năng Chạy Thử Nghiệm / Mô Phỏng (Simulated Only)
- [x] Luồng stream mẫu `mock://` trên Camera Wall khi chạy chế độ Demo.
- [x] Dữ liệu sự kiện demo ban đầu (được dán nhãn `is_simulated = True`).

## 4. Tính Năng Không Bao Gồm Trong Bản V1.0 (Deliberately Excluded)
- [ ] **Nhận diện danh tính / Khuôn mặt (Face Recognition):** Cố ý không kích hoạt để tuân thủ quyền riêng tư dữ liệu y tế và Nghị định 13/2023/NĐ-CP.
- [ ] **Chẩn đoán y khoa tự động:** Hệ thống chỉ phát hiện hình thái chuyển động hỗ trợ an toàn, không can thiệp chỉ định y khoa.
