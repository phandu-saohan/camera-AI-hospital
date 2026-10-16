# GIẢ ĐỊNH THIẾT KẾ & GIỚI HẠN VẬN HÀNH — AI HOSPITAL CAMERA V1.0

## 1. Giả Định Kỹ Thuật (Assumptions)
1. **Mạng nội bộ cách ly:** Toàn bộ hệ thống camera IP và máy chủ được giả định hoạt động trong mạng nội bộ (LAN / VLAN) được kiểm soát truy cập, không mở trực tiếp ra Internet công cộng.
2. **Đầu ghi NVR độc lập:** Đầu ghi hình NVR của bệnh viện chịu trách nhiệm ghi hình lưu trữ liên tục 24/7. Nền tảng AI Camera V1.0 chỉ trích xuất luồng phụ/luồng chính để phân tích AI và lưu trữ ảnh chụp bằng chứng khi có sự kiện phát sinh, không duplicate toàn bộ dung lượng ghi 24/7.
3. **Quyền riêng tư tối cao:** Không sử dụng nhận diện khuôn mặt bệnh nhân để tránh vi phạm các quy định về bảo vệ dữ liệu nhạy cảm y tế.

## 2. Giới Hạn Vận Hành (Operational Limitations)
1. **Phụ thuộc điều kiện môi trường:** Chất lượng phân tích AI phụ thuộc vào góc đặt camera, độ sáng tại khu vực và độ phân giải hình ảnh tối thiểu (khuyến nghị từ 1080p trở lên cho nhận diện người).
2. **Bắt buộc có sự can thiệp của con người:** Mọi cảnh báo té ngã hoặc xâm nhập đều nhằm mục đích hỗ trợ an toàn và cảnh báo sớm; không tự động gọi xe cứu thương hay can thiệp quy trình lâm sàng mà phải qua nhân viên y tế trực kiểm tra xác nhận.
