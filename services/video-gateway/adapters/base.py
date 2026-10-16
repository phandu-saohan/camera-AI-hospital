from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class CameraStreamInfo:
    def __init__(self, codec: str, resolution: str, fps: float, bitrate_kbps: Optional[int] = None):
        self.codec = codec
        self.resolution = resolution
        self.fps = fps
        self.bitrate_kbps = bitrate_kbps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "codec": self.codec,
            "resolution": self.resolution,
            "fps": self.fps,
            "bitrate_kbps": self.bitrate_kbps,
        }


class BaseCameraAdapter(ABC):
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test stream connection and return health metadata."""
        pass

    @abstractmethod
    def get_stream_url(self, stream_type: str = "main") -> str:
        """Return server-side stream URL."""
        pass
