from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.router import api_router
from app.api.v1.endpoints.health import router as health_router
from app.services.websocket_manager import ws_manager
from app.core.security import decode_token
import logging
import time
import uuid

setup_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    if settings.DEMO_MODE:
        logger.warning("DEMO MODE IS ACTIVE — simulated data will be used")
    
    # Seed demo data if needed
    try:
        from app.db.base import SessionLocal, init_db
        from app.services.demo_seeder import seed_demo_data
        init_db()
        db = SessionLocal()
        try:
            seed_demo_data(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Demo seeder / DB init error: {e}")

    # Start AI Computer Vision worker background task
    ai_task = None
    if settings.AI_ENABLED:
        try:
            import asyncio
            from app.services.ai_worker import ai_worker
            ai_task = asyncio.create_task(ai_worker.start_background_loop(interval_seconds=6.0))
            logger.info("AI Computer Vision Worker background task launched successfully.")
        except Exception as e:
            logger.error(f"Failed to launch AI worker: {e}")

    yield

    if ai_task:
        try:
            from app.services.ai_worker import ai_worker
            ai_worker.stop()
            ai_task.cancel()
        except Exception:
            pass
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Hospital Camera Surveillance Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.monotonic()
    response = await call_next(request)
    duration = (time.monotonic() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration:.1f}ms"
    return response


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )


# Mount routes
app.include_router(health_router)  # /health/* without prefix
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Authenticated WebSocket for real-time events."""
    # Authenticate before accepting
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return
    
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    user_id = payload.get("sub")
    conn_id = await ws_manager.connect(websocket, user_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection.established",
            "conn_id": conn_id,
            "demo_mode": settings.DEMO_MODE,
        })
        
        while True:
            # Keep alive - wait for client messages or ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(conn_id)
    except Exception as e:
        logger.error(f"WebSocket error {conn_id}: {e}")
        await ws_manager.disconnect(conn_id)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "docs": "/api/docs",
    }
