"""
WebSocket router for real-time updates.
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import List
import json

from jose import JWTError, jwt
from fastapi import HTTPException, status
from src.config.settings import settings
from src.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Broadcast message to all active WebSocket connections."""
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.CONNECTED:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    self.disconnect(connection)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection."""
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending personal message: {e}")
                self.disconnect(websocket)


manager = ConnectionManager()


@router.websocket("/ws/ai")
async def websocket_ai_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for AI-related real-time updates.
    Handles Kanban board updates triggered by AI actions.
    """
    try:
        # Extract and verify JWT token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008, reason="Missing authentication token")
            return

        try:
            # Decode and verify JWT token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            username: str | None = payload.get("sub")
            if username is None:
                await websocket.close(code=1008, reason="Invalid authentication token")
                return
            
            # For MVP: Accept hardcoded user
            if username != "user":
                await websocket.close(code=1008, reason="Invalid user")
                return
                
        except JWTError:
            logger.error("JWT verification failed")
            await websocket.close(code=1008, reason="Authentication failed")
            return

        # Accept the connection
        await manager.connect(websocket)

        # Keep connection alive
        while True:
            try:
                # Just keep the connection open, we don't expect messages from client
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message: {data}")
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                manager.disconnect(websocket)
                break

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=1011)


async def broadcast_kanban_update():
    """
    Broadcast a Kanban update notification to all connected clients.
    """
    message = json.dumps({
        "type": "kanban_update",
        "message": "Kanban board has been updated by AI"
    })
    await manager.broadcast(message)
