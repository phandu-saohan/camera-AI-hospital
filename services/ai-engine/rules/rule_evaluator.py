from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
import math


def point_in_polygon(x: float, y: float, polygon: List[Dict[str, float]]) -> bool:
    """Ray casting algorithm to check if (x, y) point is inside polygon."""
    n = len(polygon)
    if n < 3:
        return True  # If no polygon or invalid, consider whole frame

    inside = False
    p1 = polygon[0]
    for i in range(1, n + 1):
        p2 = polygon[i % n]
        if y > min(p1['y'], p2['y']):
            if y <= max(p1['y'], p2['y']):
                if x <= max(p1['x'], p2['x']):
                    if p1['y'] != p2['y']:
                        xinters = (y - p1['y']) * (p2['x'] - p1['x']) / (p2['y'] - p1['y']) + p1['x']
                    if p1['x'] == p2['x'] or x <= xinters:
                        inside = not inside
        p1 = p2
    return inside


class DetectionBox:
    def __init__(self, x1: float, y1: float, x2: float, y2: float, confidence: float, class_name: str = "person"):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.confidence = confidence
        self.class_name = class_name

    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    @property
    def aspect_ratio(self) -> float:
        # height / width
        w = max(self.x2 - self.x1, 1e-4)
        h = max(self.y2 - self.y1, 1e-4)
        return h / w


class AIRuleEvaluator:
    def __init__(self):
        # camera_id:rule_id -> last_triggered_datetime
        self.cooldown_cache: Dict[str, datetime] = {}

    def is_in_cooldown(self, camera_id: str, rule_id: str, cooldown_seconds: int) -> bool:
        key = f"{camera_id}:{rule_id}"
        now = datetime.now(timezone.utc)
        last = self.cooldown_cache.get(key)
        if not last:
            return False
        return (now - last) < timedelta(seconds=cooldown_seconds)

    def mark_triggered(self, camera_id: str, rule_id: str):
        key = f"{camera_id}:{rule_id}"
        self.cooldown_cache[key] = datetime.now(timezone.utc)

    def evaluate_person_detection(
        self,
        detections: List[DetectionBox],
        confidence_threshold: float,
        roi_polygon: Optional[List[Dict[str, float]]] = None,
    ) -> List[DetectionBox]:
        matched = []
        for det in detections:
            if det.class_name == "person" and det.confidence >= confidence_threshold:
                cx, cy = det.center
                if not roi_polygon or point_in_polygon(cx, cy, roi_polygon):
                    matched.append(det)
        return matched

    def evaluate_restricted_area(
        self,
        camera_id: str,
        rule_id: str,
        detections: List[DetectionBox],
        roi_polygon: List[Dict[str, float]],
        confidence_threshold: float = 0.5,
        cooldown_seconds: int = 60,
    ) -> Optional[Dict[str, Any]]:
        if self.is_in_cooldown(camera_id, rule_id, cooldown_seconds):
            return None

        violators = self.evaluate_person_detection(detections, confidence_threshold, roi_polygon)
        if violators:
            self.mark_triggered(camera_id, rule_id)
            return {
                "event_type": "restricted_area",
                "severity": "high",
                "confidence": max(v.confidence for v in violators),
                "count": len(violators),
                "description": f"Phát hiện {len(violators)} người xâm nhập khu vực hạn chế",
            }
        return None

    def evaluate_fall_detection(
        self,
        camera_id: str,
        rule_id: str,
        detections: List[DetectionBox],
        confidence_threshold: float = 0.5,
        cooldown_seconds: int = 120,
    ) -> Optional[Dict[str, Any]]:
        """Experimental safety-support detector using bounding box aspect ratio drop & rapid center displacement."""
        if self.is_in_cooldown(camera_id, rule_id, cooldown_seconds):
            return None

        # Standing human aspect ratio is typically > 1.8; lying down / fallen is < 0.8
        for det in detections:
            if det.class_name == "person" and det.confidence >= confidence_threshold:
                if det.aspect_ratio < 0.8:  # Lying horizontally
                    self.mark_triggered(camera_id, rule_id)
                    return {
                        "event_type": "fall_detection",
                        "severity": "critical",
                        "confidence": det.confidence,
                        "description": "Nghi vấn bệnh nhân té ngã (tỷ lệ cơ thể nằm ngang bất thường)",
                    }
        return None

    def evaluate_people_counting(
        self,
        detections: List[DetectionBox],
        confidence_threshold: float = 0.5,
    ) -> int:
        persons = [d for d in detections if d.class_name == "person" and d.confidence >= confidence_threshold]
        return len(persons)
