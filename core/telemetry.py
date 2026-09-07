import asyncio
import json
from typing import List
from fastapi import WebSocket

class TelemetryManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[Telemetry] Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[Telemetry] Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_event(self, event_type: str, payload: dict):
        """Broadcast real-time workflow events to connected WebSocket clients."""
        if not self.active_connections:
            return
            
        message = json.dumps({
            "event": event_type,
            "data": payload
        })
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
                
        for conn in disconnected:
            self.disconnect(conn)

telemetry = TelemetryManager()
