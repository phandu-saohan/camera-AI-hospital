# DANH MỤC TƯƠNG THÍCH CAMERA & NVR — AI HOSPITAL CAMERA V1.0

## 1. Các Hãng Thiết Bị Hỗ Trợ Đầy Đủ

| Nhà Sản Xuất | Phương Thức Kết Nối | Định Dạng Luồng | Khuyến Nghị Vận Hành |
| :--- | :--- | :--- | :--- |
| **Hikvision** | ONVIF Profile S/T, RTSP Direct | H.264 / H.265 | Luồng Substream cho Camera Wall, Main cho AI Inference |
| **Dahua** | ONVIF Profile S, RTSP Direct | H.264 / H.265 | Sử dụng cổng RTSP 554 tiêu chuẩn qua TCP |
| **Uniview (UNV)** | ONVIF Profile S, RTSP | H.264 | Bật xác thực Digest Authentication trên camera |
| **Axis Communications** | ONVIF Profile S/T/M | H.264 / H.265 | Tương thích cao với MediaMTX proxy |
| **Hanwha Vision (Samsung)** | ONVIF, RTSP | H.264 | Cần cấp phép địa chỉ IP máy chủ trong Firewall camera |
| **Đầu ghi NVR (Đa kênh)** | RTSP Channel Mapping | H.264 | Khai báo kênh dạng `/Streaming/Channels/{channel}01` |

## 2. Tiêu Chuẩn Kết Nối & An Ninh Mạng
- **Giao thức truyền dẫn:** Bắt buộc sử dụng RTSP over TCP để tránh hiện tượng mất gói tin gây giật vỡ khung hình như trên UDP.
- **Dải mạng cho phép:** Chỉ cho phép kết nối đến các địa chỉ IP nằm trong cấu hình `CAMERA_ALLOWED_SUBNETS` (ví dụ `192.168.1.0/24`). Ngăn chặn hoàn toàn lỗ hổng SSRF.
- **Không quét mạng diện rộng (No Broad Scan):** Hệ thống không tự ý phát broadcast toàn bộ mạng LAN mà chỉ thăm dò các subnet và IP được chỉ định rõ ràng.
