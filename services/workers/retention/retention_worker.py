import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RetentionWorker:
    def __init__(self, storage_dir: str = "./evidence_storage"):
        self.storage_dir = storage_dir

    def run_cleanup_cycle(self) -> Dict[str, Any]:
        """Cleans up expired evidence files and reports disk usage."""
        deleted_count = 0
        freed_bytes = 0

        now = datetime.now(timezone.utc).timestamp()
        if not os.path.exists(self.storage_dir):
            return {"deleted_files": 0, "freed_mb": 0.0}

        for root, _, files in os.walk(self.storage_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    # For demo/file-based: check file modification time > 30 days
                    if (now - stat.st_mtime) > (30 * 86400):
                        freed_bytes += stat.st_size
                        os.remove(file_path)
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Error checking file {file_path}: {e}")

        logger.info(f"Retention cycle completed: deleted {deleted_count} files, freed {freed_bytes / (1024*1024):.2f} MB")
        return {
            "deleted_files": deleted_count,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2),
        }
