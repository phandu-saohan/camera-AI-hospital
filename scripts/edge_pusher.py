# -*- coding: utf-8 -*-
"""
Edge Pusher Script: Streams physical Dahua IP camera (RTSP) to AI Hospital Camera (Cloud / Local).
Usage:
    python scripts/edge_pusher.py --api https://<your-cloudflare-tunnel>.trycloudflare.com
"""

import sys
import os
import time
import argparse
import urllib.request
import urllib.error
import json

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import cv2
except ImportError:
    print("[ERROR] OpenCV is not installed. Please run: pip install opencv-python")
    sys.exit(1)


def get_first_camera_id(base_url: str) -> str:
    """Fetch camera list from the API to get an available camera ID."""
    url = f"{base_url.rstrip('/')}/api/v1/cameras?page=1&page_size=10"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EdgePusher/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            if items:
                cam = items[0]
                print(f"[INFO] Auto-selected camera: '{cam.get('name')}' (ID: {cam.get('id')})")
                return cam.get("id")
    except Exception as e:
        print(f"[WARNING] Could not auto-fetch camera list ({e}).")
    return None


def main():
    parser = argparse.ArgumentParser(description="AI Hospital Camera - Edge RTSP Stream Pusher")
    parser.add_argument(
        "--rtsp",
        default="rtsp://admin:L2622B4F@192.168.111.168:554/cam/realmonitor?channel=1&subtype=1",
        help="RTSP URL of the physical Dahua camera (sub-stream recommended)",
    )
    parser.add_argument(
        "--api",
        default="http://localhost:8000",
        help="Base URL of the AI Hospital Camera server (e.g. https://xyz.trycloudflare.com)",
    )
    parser.add_argument(
        "--camera-id",
        default=None,
        help="Target Camera UUID (if omitted, automatically discovers first camera)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=12.0,
        help="Target transmission FPS (default: 12 FPS, optimal for cloud bandwidth)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=960,
        help="Maximum frame width (resizes high-res stream for low latency, default: 960)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=75,
        help="JPEG compression quality 1-100 (default: 75)",
    )

    args = parser.parse_args()

    base_url = args.api.rstrip("/")
    camera_id = args.camera_id

    print("=" * 65)
    print("   AI HOSPITAL CAMERA - EDGE RTSP STREAM PUSHER")
    print("=" * 65)
    print(f"[*] Camera RTSP:  {args.rtsp}")
    print(f"[*] Target API:   {base_url}")
    print(f"[*] Target FPS:   {args.fps} FPS")

    if not camera_id:
        print("[*] Finding camera ID from server...")
        camera_id = get_first_camera_id(base_url)
        if not camera_id:
            # Fallback to demo ID
            camera_id = "00000000-0000-0000-0000-000000000001"
            print(f"[!] Using default camera ID: {camera_id}")

    ingest_endpoint = f"{base_url}/api/v1/cameras/{camera_id}/ingest-frame"
    print(f"[*] Ingest URL:   {ingest_endpoint}")
    print("=" * 65)

    interval = 1.0 / args.fps
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), args.quality]

    while True:
        print(f"\n[INFO] Connecting to RTSP stream...")
        cap = cv2.VideoCapture(args.rtsp)

        if not cap.isOpened():
            print("[ERROR] Cannot open RTSP stream. Retrying in 5 seconds...")
            time.sleep(5)
            continue

        print("[SUCCESS] Camera stream connected! Streaming frames to cloud...")

        frames_sent = 0
        last_stat_time = time.time()
        stat_frames = 0

        try:
            while True:
                start_loop = time.time()

                ret, frame = cap.read()
                if not ret or frame is None:
                    print("[WARNING] Frame capture dropped. Reconnecting...")
                    break

                h, w = frame.shape[:2]
                if w > args.width:
                    scale = args.width / float(w)
                    frame = cv2.resize(frame, (args.width, int(h * scale)))

                success, encoded_jpg = cv2.imencode(".jpg", frame, encode_param)
                if not success:
                    continue

                payload = encoded_jpg.tobytes()

                # Send frame via HTTP POST
                try:
                    req = urllib.request.Request(
                        ingest_endpoint,
                        data=payload,
                        headers={
                            "Content-Type": "image/jpeg",
                            "User-Agent": "EdgePusher/1.0",
                        },
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=3.0) as resp:
                        pass
                    frames_sent += 1
                    stat_frames += 1
                except urllib.error.URLError as u_err:
                    print(f"[ERROR] Ingest push failed: {u_err}")
                    time.sleep(1.0)
                except Exception as ex:
                    print(f"[ERROR] Push error: {ex}")
                    time.sleep(1.0)

                # Status reporter every 5 seconds
                now = time.time()
                elapsed = now - last_stat_time
                if elapsed >= 5.0:
                    current_fps = stat_frames / elapsed
                    print(f"[STREAMING] Sent {frames_sent} frames | Real-time: {current_fps:.1f} FPS | Frame size: {len(payload)//1024} KB")
                    last_stat_time = now
                    stat_frames = 0

                # Rate limiting to target FPS
                took = time.time() - start_loop
                sleep_time = interval - took
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n[INFO] Streaming stopped by user.")
            cap.release()
            return
        except Exception as e:
            print(f"[EXCEPTION] Loop error: {e}")
        finally:
            cap.release()

        print("[INFO] Reconnecting in 3 seconds...")
        time.sleep(3)


if __name__ == "__main__":
    main()
