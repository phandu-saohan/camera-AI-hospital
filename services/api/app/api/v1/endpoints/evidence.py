import os
import io
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.event import EventEvidence
from app.core.config import settings
import cv2
import numpy as np

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.get("/{evidence_id}/download")
def download_evidence(
    evidence_id: uuid.UUID,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Download JPEG snapshot evidence for an event."""
    evidence = db.query(EventEvidence).filter(EventEvidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    storage_dir = os.path.abspath(settings.EVIDENCE_STORAGE_PATH)
    file_path = os.path.join(storage_dir, evidence.storage_key)

    if os.path.isfile(file_path):
        return FileResponse(file_path, media_type="image/jpeg", filename=evidence.storage_key)

    # Fallback: dynamically generate a JPEG placeholder with metadata
    img = np.zeros((360, 640, 3), dtype=np.uint8)
    img[:] = (30, 41, 59)
    cv2.putText(img, "AI HOSPITAL CAMERA - EVIDENCE", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(img, f"ID: {evidence.id}", (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (148, 163, 184), 1)
    cv2.putText(img, f"TYPE: {evidence.evidence_type.value}", (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (34, 197, 94), 1)
    cv2.putText(img, "IMAGE ARCHIVED OR SIMULATED", (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (245, 158, 11), 2)

    success, buffer = cv2.imencode(".jpg", img)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")
