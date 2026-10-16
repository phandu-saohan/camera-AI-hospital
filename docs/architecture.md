# KIẾN TRÚC HỆ THỐNG — AI HOSPITAL CAMERA V1.0

## 1. Sơ đồ Luồng Dữ liệu Tổng thể

```mermaid
flowchart TD
    subgraph Edge ["Khu vực Thiết bị Ngoại vi (Hospital Network)"]
        Cam1["Camera IP Hikvision"]
        Cam2["Camera IP Dahua"]
        Cam3["Camera IP Uniview / Axis"]
        NVR["Đầu ghi NVR 32/64 Kênh"]
    end

    subgraph VideoGateway ["Tầng Tiếp nhận & Phân phối Video"]
        Adapter["Camera Adapters (ONVIF / RTSP TCP)"]
        MediaMTX["MediaMTX Media Server (RTSP / WebRTC WHEP / HLS)"]
    end

    subgraph CoreBackend ["FastAPI Core Platform"]
        Auth["Xác thực JWT & Phân quyền RBAC"]
        CamMgmt["Quản lý Danh mục Camera & NVR"]
        WS["WebSocket Notification Hub"]
        Audit["Audit Trail Logging Service"]
    end

    subgraph AIEngine ["Tầng AI Computer Vision"]
        Scheduler["AI Task Scheduler (Priority & Target FPS)"]
        Inference["Inference Engine (CUDA / TensorRT / CPU Fallback)"]
        RuleEngine["Rule Evaluator (ROI Polygon, Tampering, Fall, Counting)"]
        Deduplication["Event Deduplication & Cooldown Manager"]
    end

    subgraph Storage ["Lưu trữ Bền vững"]
        Postgres[(PostgreSQL 16 Database)]
        EvidenceFS["Lưu trữ Bằng chứng Snapshot / Clip (SHA256)"]
    end

    subgraph ClientLayer ["Trạm Giám sát Vận hành (Browser UI)"]
        Dashboard["Bảng điều khiển Tổng quan"]
        CamWall["Màn hình Camera Wall (1/4/9/16 ô)"]
        AlertCenter["Trung tâm Tiếp nhận & Xử lý Sự cố"]
    end

    Cam1 & Cam2 & Cam3 --> Adapter
    NVR --> Adapter
    Adapter --> MediaMTX
    MediaMTX -->|RTSP Raw Stream| Scheduler
    Scheduler --> Inference
    Inference --> RuleEngine
    RuleEngine --> Deduplication
    Deduplication --> Postgres
    Deduplication --> EvidenceFS
    Deduplication --> WS
    WS --> ClientLayer
    CoreBackend --> Postgres
    MediaMTX -.->|WebRTC WHEP (Authorized Token)| CamWall
```

## 2. Các Phân Lớp Kỹ Thuật
1. **Frontend WebApp:** React 18, TypeScript, Vite, TanStack Query, Recharts, Lucide Icons.
2. **API Backend:** FastAPI, SQLAlchemy 2.0, Alembic, Pydantic V2, Uvicorn.
3. **Gateway Video:** MediaMTX đóng vai trò proxy giải mã và phát WebRTC độ trễ thấp (<500ms) vào trình duyệt mà không lộ mật khẩu camera.
4. **AI Engine:** Kiến trúc tách biệt với API chính, đảm bảo khi tác vụ suy luận nặng hoặc GPU gặp sự cố, hệ thống quản lý và giám sát vẫn hoạt động bình thường.
