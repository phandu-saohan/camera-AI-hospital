import pytest
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workers', 'evidence')))
from evidence_worker import EvidenceWorker


def test_evidence_worker_save_snapshot():
    test_dir = "./test_evidence_tmp"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    worker = EvidenceWorker(storage_dir=test_dir, retention_days=30)
    fake_image = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100  # simulated JPEG header + payload

    res = worker.save_snapshot(
        event_id="evt-12345",
        camera_id="cam-9999",
        image_bytes=fake_image,
        access_classification="restricted",
    )

    assert res["event_id"] == "evt-12345"
    assert res["file_size_bytes"] == len(fake_image)
    assert res["checksum_sha256"] is not None
    assert len(res["checksum_sha256"]) == 64
    assert res["access_classification"] == "restricted"

    # Verify physical file exists
    full_path = os.path.join(test_dir, res["storage_key"])
    assert os.path.exists(full_path)

    # Cleanup
    shutil.rmtree(test_dir)
