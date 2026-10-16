import socket
import time
from typing import Dict, Any
from .base import BaseCameraAdapter, CameraStreamInfo


class RTSPCameraAdapter(BaseCameraAdapter):
    def __init__(self, ip_address: str, port: int = 554, rtsp_url: str = ""):
        self.ip_address = ip_address
        self.port = port
        self.rtsp_url = rtsp_url

    def test_connection(self) -> Dict[str, Any]:
        start = time.monotonic()
        try:
            with socket.create_connection((self.ip_address, self.port), timeout=4.0):
                latency = (time.monotonic() - start) * 1000
                return {
                    "success": True,
                    "latency_ms": round(latency, 2),
                    "stream_info": CameraStreamInfo("H.264", "1920x1080", 25.0).to_dict(),
                    "is_simulated": False,
                    "error": None,
                }
        except socket.timeout:
            return {
                "success": False,
                "latency_ms": None,
                "stream_info": None,
                "is_simulated": False,
                "error": f"Hết thời gian kết nối tới {self.ip_address}:{self.port}",
            }
        except Exception as e:
            return {
                "success": False,
                "latency_ms": None,
                "stream_info": None,
                "is_simulated": False,
                "error": f"Lỗi kết nối cổng RTSP: {type(e).__name__}",
            }

    def get_stream_url(self, stream_type: str = "main") -> str:
        return self.rtsp_url
