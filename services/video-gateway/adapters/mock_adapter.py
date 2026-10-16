from typing import Dict, Any
from .base import BaseCameraAdapter, CameraStreamInfo


class MockCameraAdapter(BaseCameraAdapter):
    def __init__(self, camera_name: str = "Demo Camera"):
        self.camera_name = camera_name

    def test_connection(self) -> Dict[str, Any]:
        return {
            "success": True,
            "latency_ms": 12.5,
            "stream_info": CameraStreamInfo("H.264", "1920x1080", 25.0, 2048).to_dict(),
            "is_simulated": True,
            "error": None,
        }

    def get_stream_url(self, stream_type: str = "main") -> str:
        return f"mock://stream/{self.camera_name}/{stream_type}"
