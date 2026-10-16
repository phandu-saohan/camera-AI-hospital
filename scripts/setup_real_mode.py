# -*- coding: utf-8 -*-
"""
Setup Real Mode:
1. Deletes all demo cameras ([DEMO]) and simulated demo events.
2. Ensures all real cameras have is_demo = 0 and ai_enabled = 1.
3. Automatically registers all 5 real AI surveillance rules on real cameras:
   - RESTRICTED_AREA
   - FALL_DETECTION
   - CAMERA_TAMPER
   - PEOPLE_COUNTING
   - QUEUE_ESTIMATION
"""

import sqlite3
import uuid
import json
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

db_paths = ["services/api/dev.db", "dev.db"]

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue

    print(f"\n[*] Processing database: {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # 1. Delete simulated demo events and evidence
        c.execute("DELETE FROM event_evidence WHERE event_id IN (SELECT id FROM ai_events WHERE is_simulated = 1 OR description LIKE '%[DEMO%')")
        c.execute("DELETE FROM event_assignments WHERE event_id IN (SELECT id FROM ai_events WHERE is_simulated = 1 OR description LIKE '%[DEMO%')")
        c.execute("DELETE FROM event_audit_logs WHERE event_id IN (SELECT id FROM ai_events WHERE is_simulated = 1 OR description LIKE '%[DEMO%')")
        c.execute("DELETE FROM ai_events WHERE is_simulated = 1 OR description LIKE '%[DEMO%'")
        print(" -> Cleaned demo/simulated events.")

        # 2. Delete demo cameras and their associated records
        c.execute("DELETE FROM ai_rules WHERE camera_id IN (SELECT id FROM cameras WHERE is_demo = 1 OR name LIKE '%[DEMO]%')")
        c.execute("DELETE FROM camera_streams WHERE camera_id IN (SELECT id FROM cameras WHERE is_demo = 1 OR name LIKE '%[DEMO]%')")
        c.execute("DELETE FROM camera_credentials WHERE camera_id IN (SELECT id FROM cameras WHERE is_demo = 1 OR name LIKE '%[DEMO]%')")
        c.execute("DELETE FROM camera_health_logs WHERE camera_id IN (SELECT id FROM cameras WHERE is_demo = 1 OR name LIKE '%[DEMO]%')")
        c.execute("DELETE FROM cameras WHERE is_demo = 1 OR name LIKE '%[DEMO]%'")
        print(" -> Removed demo cameras.")

        # 3. Configure real cameras and deploy 5 real AI rules
        c.execute("SELECT id, name FROM cameras WHERE deleted_at IS NULL")
        cameras = c.fetchall()

        for cam_id, cam_name in cameras:
            c.execute("UPDATE cameras SET is_demo = 0, is_active = 1, ai_enabled = 1 WHERE id = ?", (cam_id,))
            print(f" -> Configured real camera: '{cam_name}' (ID: {cam_id})")

            rules_def = [
                ("RESTRICTED_AREA", "Phát hiện xâm nhập vùng cấm", 0.60, "high", 20, 
                 json.dumps([{"x": 0.05, "y": 0.1}, {"x": 0.95, "y": 0.1}, {"x": 0.95, "y": 0.9}, {"x": 0.05, "y": 0.9}]), None),
                ("FALL_DETECTION", "Cảnh báo bệnh nhân té ngã", 0.60, "critical", 20, None, None),
                ("CAMERA_TAMPER", "Cảnh báo che mắt / xáo trộn camera", 0.85, "critical", 30, None, None),
                ("PEOPLE_COUNTING", "Giám sát mật độ người lưu thông", 0.55, "medium", 30, None, json.dumps({"max_people": 2})),
                ("QUEUE_ESTIMATION", "Cảnh báo ùn tắc khu vực chờ", 0.55, "high", 45, None, json.dumps({"max_people": 3})),
            ]

            for r_type, r_name, conf, sev, cool, roi, extra in rules_def:
                c.execute("SELECT id FROM ai_rules WHERE camera_id = ? AND rule_type = ?", (cam_id, r_type))
                existing = c.fetchone()
                if not existing:
                    rule_uuid = uuid.uuid4().hex
                    c.execute("""
                        INSERT INTO ai_rules (id, camera_id, name, rule_type, is_enabled, confidence_threshold, severity, cooldown_seconds, min_duration_seconds, roi_polygon, extra_config, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 1, ?, ?, ?, 1.0, ?, ?, datetime('now'), datetime('now'))
                    """, (rule_uuid, cam_id, r_name, r_type, conf, sev, cool, roi, extra))
                    print(f"    + Created real rule: [{r_type}] {r_name}")
                else:
                    c.execute("""
                        UPDATE ai_rules SET is_enabled = 1, confidence_threshold = ?, severity = ?, cooldown_seconds = ?, roi_polygon = COALESCE(?, roi_polygon), extra_config = COALESCE(?, extra_config)
                        WHERE id = ?
                    """, (conf, sev, cool, roi, extra, existing[0]))
                    print(f"    * Updated real rule: [{r_type}] {r_name}")

        conn.commit()
        print(f"[SUCCESS] Database {db_path} is now configured in 100% REAL PRODUCTION MODE!")
    except Exception as e:
        print(f"[ERROR] {db_path}: {e}")
    finally:
        conn.close()
