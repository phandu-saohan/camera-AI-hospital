import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CameraInferenceTask:
    camera_id: str
    target_fps: float = 2.0
    priority: int = 1  # 1 = highest, 5 = lowest
    last_run: float = 0.0


class AIScheduler:
    def __init__(self, max_concurrent_streams: int = 10, backend: str = "cpu"):
        self.max_concurrent_streams = max_concurrent_streams
        self.backend = backend
        self.tasks: Dict[str, CameraInferenceTask] = {}
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self.is_running = False

    def register_camera(self, camera_id: str, target_fps: float = 2.0, priority: int = 1):
        self.tasks[camera_id] = CameraInferenceTask(
            camera_id=camera_id,
            target_fps=target_fps,
            priority=priority,
            last_run=0.0,
        )
        logger.info(f"Registered camera {camera_id} in AI scheduler at {target_fps} FPS, priority {priority}")

    def unregister_camera(self, camera_id: str):
        if camera_id in self.tasks:
            del self.tasks[camera_id]
            logger.info(f"Unregistered camera {camera_id} from AI scheduler")

    def get_ready_cameras(self) -> List[str]:
        now = time.monotonic()
        ready = []
        for cid, task in sorted(self.tasks.items(), key=lambda x: x[1].priority):
            interval = 1.0 / max(task.target_fps, 0.1)
            if (now - task.last_run) >= interval:
                task.last_run = now
                ready.append(cid)
        return ready

    def get_status(self) -> Dict[str, Any]:
        return {
            "backend": self.backend,
            "registered_cameras": len(self.tasks),
            "max_concurrent_streams": self.max_concurrent_streams,
            "queue_depth": self.queue.qsize(),
            "is_running": self.is_running,
        }
