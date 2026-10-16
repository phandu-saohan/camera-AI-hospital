"""AI Person Tracker for Hospital Camera Surveillance.
Implements Multi-Object Tracking (MOT) using Centroid & IoU association with Hungarian algorithm.
Maintains persistent track IDs, dwell time, motion trajectory, and renders surveillance HUD overlays.
"""

import time
import math
import collections
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment


class TrackedPerson:
    def __init__(self, track_id: int, bbox: Tuple[int, int, int, int], confidence: float = 0.85):
        self.track_id = track_id
        self.bbox = list(bbox)  # [x, y, w, h]
        self.confidence = confidence
        self.first_seen = time.time()
        self.last_seen = time.time()
        self.disappeared_frames = 0
        self.history = collections.deque(maxlen=30)  # past bottom-center (feet) positions
        
        # Calculate initial foot position
        x, y, w, h = bbox
        foot_x = int(x + w / 2)
        foot_y = int(y + h)
        self.history.append((foot_x, foot_y))
        
        self.velocity = 0.0  # pixels per second
        self.is_stationary = False
        self.stationary_since = None

    def update(self, bbox: Tuple[int, int, int, int], confidence: float):
        now = time.time()
        dt = max(0.001, now - self.last_seen)
        self.last_seen = now
        self.disappeared_frames = 0
        self.confidence = 0.7 * self.confidence + 0.3 * confidence

        x, y, w, h = bbox
        new_foot_x = int(x + w / 2)
        new_foot_y = int(y + h)

        if len(self.history) > 0:
            last_x, last_y = self.history[-1]
            dist = math.hypot(new_foot_x - last_x, new_foot_y - last_y)
            inst_speed = dist / dt
            self.velocity = 0.6 * self.velocity + 0.4 * inst_speed
            
            # Check stationary status (moved < 15px over last updates)
            if self.velocity < 20.0:
                if self.stationary_since is None:
                    self.stationary_since = now
                self.is_stationary = True
            else:
                self.stationary_since = None
                self.is_stationary = False

        self.bbox = list(bbox)
        self.history.append((new_foot_x, new_foot_y))

    @property
    def dwell_seconds(self) -> float:
        return time.time() - self.first_seen

    @property
    def dwell_time_str(self) -> str:
        s = int(self.dwell_seconds)
        mins = s // 60
        secs = s % 60
        return f"{mins:02d}:{secs:02d}s"


class PersonTracker:
    def __init__(self, max_disappeared: int = 20, max_distance: float = 120.0):
        self.next_track_id = 1
        self.tracks: Dict[int, TrackedPerson] = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.total_counted = 0
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=36, detectShadows=False)

    def detect_persons(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect candidate persons from frame using motion contours and aspect ratio."""
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        fg_mask = self.bg_subtractor.apply(blurred)
        _, thresh = cv2.threshold(fg_mask, 160, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 1800:
                continue

            bx, by, bw, bh = cv2.boundingRect(cnt)
            aspect_ratio = bh / float(bw)

            # Person silhouette typically has height > width (aspect ratio 1.1 to 4.2)
            if 0.9 <= aspect_ratio <= 4.5 and bh > 50:
                conf = min(0.96, 0.70 + (area / 120000.0) * 0.25)
                detections.append({
                    "bbox": [bx, by, bw, bh],
                    "centroid": (bx + bw / 2, by + bh / 2),
                    "confidence": round(float(conf), 2),
                    "is_fallen": aspect_ratio < 0.85 and area > 4000,
                })

        return detections

    def update(self, detections: List[Dict[str, Any]]) -> List[TrackedPerson]:
        """Update tracker with new frame detections using Hungarian distance matching."""
        # Increment disappeared for all existing tracks
        for track in self.tracks.values():
            track.disappeared_frames += 1

        active_track_ids = list(self.tracks.keys())

        if not detections:
            # Clean up dead tracks
            self._cleanup_tracks()
            return list(self.tracks.values())

        if not active_track_ids:
            # Register all detections as new tracks
            for det in detections:
                self._register_track(det["bbox"], det["confidence"])
            return list(self.tracks.values())

        # Build distance cost matrix between existing track centroids and detection centroids
        cost_matrix = np.zeros((len(active_track_ids), len(detections)), dtype=np.float32)

        for i, tid in enumerate(active_track_ids):
            track = self.tracks[tid]
            tx, ty, tw, th = track.bbox
            tc_x, tc_y = tx + tw / 2, ty + th / 2

            for j, det in enumerate(detections):
                dx, dy = det["centroid"]
                # Euclidean distance
                dist = math.hypot(tc_x - dx, tc_y - dy)
                cost_matrix[i, j] = dist

        # Hungarian algorithm matching
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        used_rows = set()
        used_cols = set()

        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] <= self.max_distance:
                tid = active_track_ids[r]
                self.tracks[tid].update(detections[c]["bbox"], detections[c]["confidence"])
                used_rows.add(r)
                used_cols.add(c)

        # Register unmatched detections as new tracks
        for j, det in enumerate(detections):
            if j not in used_cols:
                self._register_track(det["bbox"], det["confidence"])

        self._cleanup_tracks()
        return list(self.tracks.values())

    def _register_track(self, bbox: List[int], confidence: float):
        track = TrackedPerson(self.next_track_id, tuple(bbox), confidence)
        self.tracks[self.next_track_id] = track
        self.next_track_id += 1
        self.total_counted += 1

    def _cleanup_tracks(self):
        dead_ids = [tid for tid, track in self.tracks.items() if track.disappeared_frames > self.max_disappeared]
        for tid in dead_ids:
            del self.tracks[tid]

    def draw_tracking_overlay(self, frame: np.ndarray, show_hud: bool = True) -> np.ndarray:
        """Draw surveillance tracking HUD, bounding boxes, labels, and motion trails on frame."""
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        active_tracks = [t for t in self.tracks.values() if t.disappeared_frames == 0]

        # 1. Draw motion trails (footprints)
        for track in active_tracks:
            pts = list(track.history)
            if len(pts) >= 2:
                for idx in range(1, len(pts)):
                    alpha = idx / float(len(pts))  # Fading trail
                    thickness = max(1, int(3 * alpha))
                    color = (int(34 * alpha), int(197 * alpha), int(94 * alpha))  # Emerald fading
                    cv2.line(annotated, pts[idx - 1], pts[idx], color, thickness, cv2.LINE_AA)

        # 2. Draw Bounding Boxes with futuristic corner brackets & badges
        for track in active_tracks:
            bx, by, bw, bh = [int(v) for v in track.bbox]
            # Ensure within frame bounds
            bx = max(0, min(w - 1, bx))
            by = max(0, min(h - 1, by))
            bw = min(w - bx, bw)
            bh = min(h - by, bh)

            # Color scheme:
            # Emerald green for moving, Amber/Orange for stationary/dwelling, Red for fallen
            if getattr(track, 'is_fallen', False):
                box_color = (0, 0, 239)  # Red
                status_text = "NGHI VẤN TÉ NGÃ"
            elif track.is_stationary and track.dwell_seconds > 8.0:
                box_color = (0, 165, 255)  # Amber
                status_text = f"ĐỨNG YÊN ({track.dwell_time_str})"
            else:
                box_color = (34, 197, 94)  # Emerald
                status_text = f"DI CHUYỂN ({track.dwell_time_str})"

            # Draw sleek Corner Brackets instead of basic solid rectangle
            self._draw_corner_rect(annotated, (bx, by, bw, bh), box_color, corner_len=18, thickness=2)

            # Center foot point
            foot_x = bx + bw // 2
            foot_y = by + bh
            cv2.circle(annotated, (foot_x, foot_y), 3, box_color, -1)

            # Top Badge Header: [#ID 01] NGƯỜI (92%)
            id_text = f"#ID {track.track_id:02d} | NGUOI {int(track.confidence * 100)}%"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.45
            (tw, th), _ = cv2.getTextSize(id_text, font, font_scale, 1)

            # Badge background pill
            badge_y = max(th + 8, by - 8)
            cv2.rectangle(
                annotated,
                (bx, badge_y - th - 6),
                (bx + tw + 12, badge_y + 4),
                (15, 23, 42),
                -1
            )
            cv2.rectangle(
                annotated,
                (bx, badge_y - th - 6),
                (bx + tw + 12, badge_y + 4),
                box_color,
                1
            )
            cv2.putText(
                annotated,
                id_text,
                (bx + 6, badge_y - 2),
                font,
                font_scale,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

            # Status pill below badge: ⏱ 00:14s
            status_font_scale = 0.38
            (sw, sh), _ = cv2.getTextSize(status_text, font, status_font_scale, 1)
            cv2.rectangle(
                annotated,
                (bx, by + bh + 4),
                (bx + sw + 10, by + bh + sh + 12),
                (15, 23, 42),
                -1
            )
            cv2.rectangle(
                annotated,
                (bx, by + bh + 4),
                (bx + sw + 10, by + bh + sh + 12),
                (51, 65, 85),
                1
            )
            cv2.putText(
                annotated,
                status_text,
                (bx + 5, by + bh + sh + 7),
                font,
                status_font_scale,
                box_color,
                1,
                cv2.LINE_AA
            )

        # 3. Top-right HUD Bar
        if show_hud:
            hud_text = f"TRACKING: {len(active_tracks)} NGUOI | TONG: {self.total_counted}"
            (hw, hh), _ = cv2.getTextSize(hud_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            # HUD pill
            cv2.rectangle(annotated, (w - hw - 30, 10), (w - 10, 36), (15, 23, 42), -1)
            cv2.rectangle(annotated, (w - hw - 30, 10), (w - 10, 36), (34, 197, 94), 1)
            # Green pulsing dot
            cv2.circle(annotated, (w - hw - 18, 23), 4, (34, 197, 94), -1)
            cv2.putText(
                annotated,
                hud_text,
                (w - hw - 8, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (248, 250, 252),
                1,
                cv2.LINE_AA
            )

        return annotated

    def _draw_corner_rect(self, img: np.ndarray, bbox: Tuple[int, int, int, int], color: Tuple[int, int, int], corner_len: int = 16, thickness: int = 2):
        """Draw aesthetic corner brackets around bbox."""
        x, y, w, h = bbox
        d = min(corner_len, w // 3, h // 3)

        # Top-left
        cv2.line(img, (x, y), (x + d, y), color, thickness)
        cv2.line(img, (x, y), (x, y + d), color, thickness)

        # Top-right
        cv2.line(img, (x + w, y), (x + w - d, y), color, thickness)
        cv2.line(img, (x + w, y), (x + w, y + d), color, thickness)

        # Bottom-left
        cv2.line(img, (x, y + h), (x + d, y + h), color, thickness)
        cv2.line(img, (x, y + h), (x, y + h - d), color, thickness)

        # Bottom-right
        cv2.line(img, (x + w, y + h), (x + w - d, y + h), color, thickness)
        cv2.line(img, (x + w, y + h), (x + w, y + h - d), color, thickness)


# Global camera tracker registry (camera_id_str -> PersonTracker)
camera_trackers: Dict[str, PersonTracker] = {}


def get_or_create_tracker(camera_id: str) -> PersonTracker:
    if camera_id not in camera_trackers:
        camera_trackers[camera_id] = PersonTracker()
    return camera_trackers[camera_id]
