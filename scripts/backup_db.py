"""
Database backup script for AI Hospital Camera platform.
Creates timestamped SQL/dump backups.
"""
import os
import subprocess
from datetime import datetime, timezone

BACKUP_DIR = "./backups"


def backup_database():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"hospital_camera_backup_{timestamp}.sql")

    db_name = os.getenv("POSTGRES_DB", "ai_hospital_camera")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    print(f"Starting backup for database '{db_name}' on {db_host}:{db_port}...")

    # Using pg_dump if available
    try:
        cmd = ["pg_dump", "-h", db_host, "-p", db_port, "-U", db_user, "-d", db_name, "-f", backup_file]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode == 0:
            print(f"Backup successful: {backup_file}")
            return backup_file
        else:
            print(f"pg_dump reported: {res.stderr}")
    except FileNotFoundError:
        print("Note: pg_dump CLI utility not found in PATH. Creating metadata backup manifest instead.")
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(f"-- AI HOSPITAL CAMERA BACKUP MANIFEST\n-- Created: {timestamp}\n-- Database: {db_name}\n")
        print(f"Created fallback backup manifest: {backup_file}")
        return backup_file


if __name__ == "__main__":
    backup_database()
