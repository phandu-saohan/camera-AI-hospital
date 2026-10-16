from fastapi import APIRouter
from app.api.v1.endpoints import auth, cameras, events, health, evidence, ai, notifications, users, departments

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(cameras.router)
api_router.include_router(events.router)
api_router.include_router(evidence.router)
api_router.include_router(ai.router)
api_router.include_router(notifications.router)
api_router.include_router(users.router)
api_router.include_router(departments.router)
