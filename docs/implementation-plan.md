# KẾ HOẠCH TRIỂN KHAI THEO CÁC MỐC (IMPLEMENTATION PLAN)

## Milestone 0: Khảo sát & Đánh giá Môi trường
- [x] Kiểm tra phần cứng CPU, RAM, dung lượng đĩa C:, phát hiện tình trạng GPU và Docker.
- [x] Xác định chiến lược suy thoái an toàn: Hỗ trợ cả CPU Fallback và GPU Acceleration.

## Milestone 1: Nền tảng Core Backend & CSDL
- [x] Thiết lập kiến trúc FastAPI, Pydantic V2, SQLAlchemy 2.0, Alembic.
- [x] Thiết lập 19 bảng thực thể dữ liệu theo chuẩn ERD y tế.
- [x] Xây dựng hệ thống xác thực JWT, mã hóa bcrypt và phân quyền RBAC đa cấp.
- [x] Xây dựng endpoint kiểm tra sức khỏe (`/health/live`, `/health/ready`, `/metrics`).

## Milestone 2: Quản lý Camera & NVR
- [x] Xây dựng API CRUD danh mục camera, NVR, phân cấp khoa phòng và tòa nhà.
- [x] Xây dựng adapter RTSP TCP và thăm dò ONVIF với subnet allowlist an toàn.
- [x] Xây dựng kiểm tra kết nối camera đo độ trễ và lưu nhật ký sức khỏe.
- [x] Chế độ Demo Mode độc lập.

## Milestone 3: Tường Camera & Gateway Phân phối Luồng
- [x] Tích hợp cấu hình MediaMTX proxy cho luồng RTSP / WebRTC WHEP / HLS.
- [x] Bảo vệ URL RTSP và thông tin xác thực trên server, không lộ ra client.
- [x] Xây dựng giao diện Camera Wall với các bố cục 1, 4, 9, 16 ô.

## Milestone 4 & 6: AI Computer Vision & Động cơ Quy tắc
- [x] Phát hiện người với ngưỡng tin cậy.
- [x] Giám sát xâm nhập khu vực hạn chế với đa giác ROI (Ray-Casting).
- [x] Hỗ trợ cảnh báo nguy cơ té ngã bệnh nhân (Aspect Ratio analysis).
- [x] Đếm người và ước tính hàng đợi.
- [x] Cơ chế chống báo động lặp Cooldown và AI Task Scheduler theo FPS.

## Milestone 5: Vận hành Sự cố & Bằng chứng
- [x] Chu trình sự cố: Tiếp nhận -> Phân công -> Hoàn tất / Đánh dấu Báo động giả.
- [x] Lưu trữ snapshot bằng chứng với mã băm toàn vẹn SHA-256.
- [x] URL truy cập tạm thời có hạn 15 phút.
- [x] Kênh thông báo WebSocket thời gian thực.

## Milestone 7 & 8: Kiểm thử Toàn diện & Báo cáo Nghiệm thu
- [x] 23/23 Automated Tests (Unit, Integration, End-to-End) PASSED 100%.
- [x] Frontend Web biên dịch thành công 100%.
- [x] Đo kiểm năng lực phần cứng thực tế (Real Benchmark Report).
- [x] Hoàn thiện 14 tài liệu kỹ thuật và hướng dẫn vận hành tiếng Việt.
