"""WebSocket endpoint for live run events."""
import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()

# run_id -> set of websocket connections
connections: Dict[str, Set[WebSocket]] = {}


async def broadcast_run_event(run_id: str, event: dict):
    """Broadcast an event to all connected WebSocket clients for a run."""
    if run_id in connections:
        disconnected = set()
        for ws in connections[run_id]:
            try:
                await ws.send_json(event)
            except Exception:
                disconnected.add(ws)
        connections[run_id] -= disconnected


@ws_router.websocket("/ws/runs/{run_id}")
async def run_events_websocket(websocket: WebSocket, run_id: str):
    await websocket.accept()
    if run_id not in connections:
        connections[run_id] = set()
    connections[run_id].add(websocket)
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "run_id": run_id,
            "message": "WebSocket connected for run events",
        })
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        if run_id in connections:
            connections[run_id].discard(websocket)
            if not connections[run_id]:
                del connections[run_id]
