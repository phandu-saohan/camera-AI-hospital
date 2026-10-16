import pytest
from app.models.ai import AIRuleType
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ai-engine')))
from rules.rule_evaluator import (
    AIRuleEvaluator,
    DetectionBox,
    point_in_polygon,
)


def test_point_in_polygon():
    polygon = [
        {"x": 0.0, "y": 0.0},
        {"x": 10.0, "y": 0.0},
        {"x": 10.0, "y": 10.0},
        {"x": 0.0, "y": 10.0},
    ]
    # Center
    assert point_in_polygon(5.0, 5.0, polygon) is True
    # Outside
    assert point_in_polygon(15.0, 5.0, polygon) is False
    assert point_in_polygon(-1.0, 5.0, polygon) is False


def test_person_detection_filtering():
    evaluator = AIRuleEvaluator()
    detections = [
        DetectionBox(0, 0, 2, 4, confidence=0.8, class_name="person"),
        DetectionBox(0, 0, 2, 4, confidence=0.3, class_name="person"),  # low confidence
        DetectionBox(0, 0, 5, 5, confidence=0.9, class_name="chair"),   # non-person
    ]

    matched = evaluator.evaluate_person_detection(detections, confidence_threshold=0.5)
    assert len(matched) == 1
    assert matched[0].confidence == 0.8


def test_restricted_area_intrusion():
    evaluator = AIRuleEvaluator()
    roi = [
        {"x": 0.0, "y": 0.0},
        {"x": 1.0, "y": 0.0},
        {"x": 1.0, "y": 1.0},
        {"x": 0.0, "y": 1.0},
    ]

    # Person inside ROI
    detections = [DetectionBox(0.2, 0.2, 0.4, 0.6, confidence=0.85, class_name="person")]
    event = evaluator.evaluate_restricted_area("cam-1", "rule-1", detections, roi, confidence_threshold=0.5, cooldown_seconds=60)
    assert event is not None
    assert event["event_type"] == "restricted_area"
    assert event["severity"] == "high"

    # Cooldown should suppress immediate duplicate trigger
    event_repeat = evaluator.evaluate_restricted_area("cam-1", "rule-1", detections, roi, confidence_threshold=0.5, cooldown_seconds=60)
    assert event_repeat is None


def test_fall_detection_aspect_ratio():
    evaluator = AIRuleEvaluator()
    # Standing person: height = 1.6, width = 0.5 -> aspect ratio = 3.2
    standing = [DetectionBox(0.2, 0.2, 0.7, 1.8, confidence=0.9, class_name="person")]
    assert evaluator.evaluate_fall_detection("cam-2", "rule-2", standing) is None

    # Fallen person: height = 0.4, width = 1.2 -> aspect ratio = 0.33
    fallen = [DetectionBox(0.1, 0.5, 1.3, 0.9, confidence=0.82, class_name="person")]
    event = evaluator.evaluate_fall_detection("cam-2", "rule-2", fallen)
    assert event is not None
    assert event["event_type"] == "fall_detection"
    assert event["severity"] == "critical"
