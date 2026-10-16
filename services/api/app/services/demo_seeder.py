"""Seeds demo data for development. All demo data is clearly marked."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.models.location import Department, Location
from app.models.camera import Camera, CameraProtocol, CameraStatus
from app.models.ai import AIModel, AIRule, AIRuleType
from app.models.event import AIEvent, EventSeverity, EventStatus
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)


def seed_demo_data(db: Session) -> None:
    """Idempotent demo data seeder."""
    if db.query(User).filter(User.email == "admin@hospital.demo").first():
        logger.info("Demo data already seeded, skipping.")
        return
    
    logger.info("Seeding demo data (all marked as DEMO)...")
    
    # Permissions
    permissions = {}
    for resource in ["cameras", "events", "users", "ai_rules", "reports", "audit_logs"]:
        for action in ["read", "write", "delete", "admin"]:
            perm = Permission(
                name=f"{resource}:{action}",
                resource=resource,
                action=action,
                description=f"{action.capitalize()} access to {resource}",
            )
            db.add(perm)
            permissions[f"{resource}:{action}"] = perm
    db.flush()
    
    # Roles
    admin_role = Role(name="Administrator", description="Full system access", is_system=True)
    operator_role = Role(name="Operator", description="Camera and event management", is_system=True)
    viewer_role = Role(name="Viewer", description="Read-only access", is_system=True)
    db.add_all([admin_role, operator_role, viewer_role])
    db.flush()
    
    # Role permissions
    for resource in ["cameras", "events", "users", "ai_rules", "reports", "audit_logs"]:
        rp = RolePermission(role_id=admin_role.id, permission_id=permissions[f"{resource}:admin"].id)
        db.add(rp)
    
    for resource in ["cameras", "events", "ai_rules", "reports"]:
        rp = RolePermission(role_id=operator_role.id, permission_id=permissions[f"{resource}:write"].id)
        db.add(rp)
    
    for resource in ["cameras", "events", "reports"]:
        rp = RolePermission(role_id=viewer_role.id, permission_id=permissions[f"{resource}:read"].id)
        db.add(rp)
    
    db.flush()
    
    # Admin user
    admin = User(
        email="admin@hospital.demo",
        full_name="Quản trị viên Demo",
        hashed_password=get_password_hash("Admin@123456"),
        is_active=True,
        is_superuser=True,
    )
    db.add(admin)
    db.flush()
    db.add(UserRole(user_id=admin.id, role_id=admin_role.id))
    
    # Operator user
    operator = User(
        email="operator@hospital.demo",
        full_name="Nhân viên Vận hành Demo",
        hashed_password=get_password_hash("Operator@123"),
        is_active=True,
        is_superuser=False,
    )
    db.add(operator)
    db.flush()
    db.add(UserRole(user_id=operator.id, role_id=operator_role.id))
    
    # Departments
    departments = [
        Department(name="Cấp cứu", code="ER", description="Khoa cấp cứu"),
        Department(name="Nội trú", code="IPD", description="Khoa nội trú"),
        Department(name="Phẫu thuật", code="OT", description="Phòng mổ"),
        Department(name="Hành lang", code="CORR", description="Hành lang và khu vực chung"),
        Department(name="Bãi đỗ xe", code="PARK", description="Bãi đỗ xe"),
    ]
    db.add_all(departments)
    db.flush()
    
    # Locations
    loc1 = Location(department_id=departments[0].id, name="Cổng vào cấp cứu", building="A", floor="1", room="ER-01")
    loc2 = Location(department_id=departments[3].id, name="Hành lang tầng 1", building="A", floor="1", room="HALL-1A")
    loc3 = Location(department_id=departments[4].id, name="Bãi đỗ xe B", building="B", floor="0", room="PARK-B")
    db.add_all([loc1, loc2, loc3])
    db.flush()

    from app.core.config import settings
    if not settings.DEMO_MODE:
        db.commit()
        logger.info("Production mode: System roles, permissions and administrator initialized (demo cameras skipped).")
        return

    # Demo cameras (clearly marked with is_demo=True)
    cameras = [
        Camera(
            name="[DEMO] Camera Cổng vào ER",
            protocol=CameraProtocol.MOCK,
            location_id=loc1.id,
            status=CameraStatus.ONLINE,
            is_active=True,
            is_demo=True,
            ai_enabled=True,
            stream_resolution="1920x1080",
            stream_fps=25.0,
            stream_codec="H.264",
            tags=["entrance", "high-priority"],
        ),
        Camera(
            name="[DEMO] Camera Hành lang A1",
            protocol=CameraProtocol.MOCK,
            location_id=loc2.id,
            status=CameraStatus.ONLINE,
            is_active=True,
            is_demo=True,
            ai_enabled=True,
            stream_resolution="1280x720",
            stream_fps=15.0,
            stream_codec="H.264",
            tags=["corridor"],
        ),
        Camera(
            name="[DEMO] Camera Bãi đỗ xe",
            protocol=CameraProtocol.MOCK,
            location_id=loc3.id,
            status=CameraStatus.OFFLINE,
            is_active=True,
            is_demo=True,
            ai_enabled=False,
            last_error="Simulated offline for demo",
            tags=["parking"],
        ),
        Camera(
            name="[DEMO] Camera Phòng chờ",
            protocol=CameraProtocol.MOCK,
            status=CameraStatus.ONLINE,
            is_active=True,
            is_demo=True,
            ai_enabled=True,
            stream_resolution="1920x1080",
            stream_fps=25.0,
            stream_codec="H.265",
            tags=["waiting", "people-counting"],
        ),
    ]
    db.add_all(cameras)
    db.flush()
    
    # AI Model
    ai_model = AIModel(
        name="YOLOv8n Person Detection (Demo)",
        version="8.0.0-demo",
        model_type="person_detection",
        backend="cpu",
        is_active=True,
        capabilities=["person_detection", "people_counting"],
    )
    db.add(ai_model)
    db.flush()
    
    # AI Rules
    rule1 = AIRule(
        camera_id=cameras[0].id,
        model_id=ai_model.id,
        name="[DEMO] Phát hiện xâm nhập khu vực cấm",
        rule_type=AIRuleType.RESTRICTED_AREA,
        is_enabled=True,
        confidence_threshold=0.6,
        severity="high",
        cooldown_seconds=30,
        roi_polygon=[{"x": 0.1, "y": 0.1}, {"x": 0.5, "y": 0.1}, {"x": 0.5, "y": 0.9}, {"x": 0.1, "y": 0.9}],
    )
    rule2 = AIRule(
        camera_id=cameras[1].id,
        model_id=ai_model.id,
        name="[DEMO] Đếm người hành lang",
        rule_type=AIRuleType.PEOPLE_COUNTING,
        is_enabled=True,
        confidence_threshold=0.5,
        severity="low",
        cooldown_seconds=60,
    )
    rule3 = AIRule(
        camera_id=cameras[3].id,
        model_id=ai_model.id,
        name="[DEMO] Giám sát ùn tắc hàng đợi tiếp đón",
        rule_type=AIRuleType.QUEUE_ESTIMATION,
        is_enabled=True,
        confidence_threshold=0.5,
        severity="medium",
        cooldown_seconds=45,
        extra_config={"max_people": 2, "min_dwell_seconds": 10.0},
    )
    db.add_all([rule1, rule2, rule3])
    db.flush()
    
    # Demo events (clearly marked as SIMULATED)
    import random
    from datetime import timedelta
    event_types = [("restricted_area", EventSeverity.HIGH), ("person_detected", EventSeverity.LOW), 
                   ("camera_tamper", EventSeverity.CRITICAL), ("person_detected", EventSeverity.LOW)]
    for i, (etype, sev) in enumerate(event_types):
        ev = AIEvent(
            camera_id=cameras[i % len(cameras)].id,
            event_type=etype,
            status=EventStatus.NEW if i < 2 else EventStatus.RESOLVED,
            severity=sev,
            is_simulated=True,  # MUST be set for all demo events
            confidence=round(0.65 + random.random() * 0.3, 2),
            model_version="demo",
            description=f"[DEMO - SIMULATED] Sự kiện demo số {i+1}",
            occurred_at=datetime.now(timezone.utc) - timedelta(minutes=30 * i),
        )
        db.add(ev)
    
    db.commit()
    logger.info("Demo data seeded successfully. Login: admin@hospital.demo / Admin@123456")
