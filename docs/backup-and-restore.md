# QUY TRÌNH SAO LƯU & PHỤC HỒI DỮ LIỆU — AI HOSPITAL CAMERA V1.0

## 1. Chiến Lược Sao Lưu (Backup Strategy)

- **Cơ sở dữ liệu (Metadata, Camera, Sự kiện, Audit):**
  - Sao lưu tự động hàng ngày lúc 02:00 sáng bằng lệnh `python scripts/backup_db.py`.
  - Lưu trữ định dạng SQL dump có nén gzip.
  - Luân chuyển: Giữ 7 bản sao lưu ngày gần nhất, 4 bản sao lưu tuần và 12 bản sao lưu tháng.
- **Thư mục Bằng chứng (Evidence Storage):**
  - Sử dụng rsync hoặc snapshot ổ cứng SAN/NAS định kỳ.

---

## 2. Lệnh Thực Thi Sao Lưu Thủ Công

```bash
# Thực hiện sao lưu ngay lập tức
python scripts/backup_db.py

# Hoặc qua Docker Compose trực tiếp từ container PostgreSQL:
docker exec -t hospital_postgres pg_dump -U postgres ai_hospital_camera > ./backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 3. Quy Trình Phục Hồi Khi Có Sự Cố (Disaster Recovery)

```bash
# 1. Tạm dừng các dịch vụ ghi dữ liệu
docker compose stop api ai-engine-gpu

# 2. Khôi phục cơ sở dữ liệu từ file backup SQL
docker exec -i hospital_postgres psql -U postgres -d ai_hospital_camera < ./backups/hospital_camera_backup_YYYYMMDD_HHMMSS.sql

# 3. Khởi động lại toàn bộ dịch vụ
docker compose up -d

# 4. Kiểm tra tính toàn vẹn hệ thống
curl http://localhost:8000/health/ready
```
