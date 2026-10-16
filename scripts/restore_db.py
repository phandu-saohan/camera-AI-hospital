"""
Database restore script for AI Hospital Camera platform.
Restores database from an existing SQL backup file.
"""
import os
import sys
import subprocess


def restore_database(backup_file: str):
    if not os.path.exists(backup_file):
        print(f"Error: Backup file '{backup_file}' does not exist.")
        return False

    db_name = os.getenv("POSTGRES_DB", "ai_hospital_camera")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    print(f"Restoring database '{db_name}' from {backup_file}...")
    try:
        cmd = ["psql", "-h", db_host, "-p", db_port, "-U", db_user, "-d", db_name, "-f", backup_file]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0:
            print(f"Restore completed successfully from {backup_file}")
            return True
        else:
            print(f"psql error: {res.stderr}")
            return False
    except FileNotFoundError:
        print("Note: psql CLI utility not found in PATH.")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        restore_database(sys.argv[1])
    else:
        print("Usage: python scripts/restore_db.py <path_to_backup_sql>")
