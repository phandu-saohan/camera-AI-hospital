# Import all models so Alembic can discover them
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.models.location import Department, Location
from app.models.camera import Camera, CameraStream, CameraCredential, CameraHealthLog, Recorder
from app.models.ai import AIModel, AIRule
from app.models.event import AIEvent, EventEvidence, EventAssignment, EventAuditLog
from app.models.audit import AuditLog, SystemSetting

__all__ = [
    "User", "Role", "Permission", "UserRole", "RolePermission",
    "Department", "Location",
    "Camera", "CameraStream", "CameraCredential", "CameraHealthLog", "Recorder",
    "AIModel", "AIRule",
    "AIEvent", "EventEvidence", "EventAssignment", "EventAuditLog",
    "AuditLog", "SystemSetting",
]
