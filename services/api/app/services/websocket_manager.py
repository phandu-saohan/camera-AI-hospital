import json
import logging
from typing import Dict, Set
from fastapi import WebSocket
import uuid

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages authenticated WebSocket connections and broadcasts."""
    
    def __init__(self):
        # Map: connection_id -> {websocket, user_id, subscriptions}
        self._connections: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        await websocket.accept()
        conn_id = str(uuid.uuid4())
        self._connections[conn_id] = {
            "websocket": websocket,
            "user_id": user_id,
        }
        logger.info(f"WebSocket connected: {conn_id} user={user_id}")
        return conn_id
    
    async def disconnect(self, conn_id: str):
        if conn_id in self._connections:
            del self._connections[conn_id]
            logger.info(f"WebSocket disconnected: {conn_id}")
    
    async def broadcast(self, message: dict):
        """Broadcast to all authenticated connections."""
        disconnected = []
        for conn_id, conn in self._connections.items():
            try:
                await conn["websocket"].send_json(message)
            except Exception as e:
                logger.warning(f"WS send failed for {conn_id}: {e}")
                disconnected.append(conn_id)
        for conn_id in disconnected:
            await self.disconnect(conn_id)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send to all connections for a specific user."""
        for conn_id, conn in list(self._connections.items()):
            if conn["user_id"] == user_id:
                try:
                    await conn["websocket"].send_json(message)
                except Exception:
                    await self.disconnect(conn_id)
    
    @property
    def active_count(self) -> int:
        return len(self._connections)


# Singleton instance
ws_manager = WebSocketManager()
