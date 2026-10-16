import logging
import subprocess
from typing import Dict, Any

logger = logging.getLogger(__name__)

_ai_state = {"ready": False, "backend": "none", "gpu_devices": [], "workers": 0}


def detect_gpu() -> list:
    """Detect available NVIDIA GPUs. Returns empty list if none available."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total,driver_version", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            gpus = []
            for line in result.stdout.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 4:
                    gpus.append({
                        "index": int(parts[0]),
                        "name": parts[1],
                        "memory_mb": int(parts[2]),
                        "driver": parts[3],
                    })
            return gpus
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.info(f"GPU detection: {e} — no GPU available")
    return []


def get_ai_status() -> Dict[str, Any]:
    """Return current AI engine status without crashing if unavailable."""
    gpus = detect_gpu()
    return {
        "ready": True,  # API itself is ready; AI workers may be degraded
        "backend": "cuda" if gpus else "cpu",
        "gpu_available": len(gpus) > 0,
        "gpu_devices": gpus,
        "active_workers": 0,  # Updated by actual worker registration
        "queue_depth": 0,
    }
