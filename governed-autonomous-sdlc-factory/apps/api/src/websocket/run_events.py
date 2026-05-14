"""WebSocket endpoint for live run events with event bus integration."""
import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from src.core.event_bus import EventBusManager, Event, replay_events
from src.core.logging import get_logger

ws_router = APIRouter()
logger = get_logger("websocket")

# run_id -> set of websocket connections
connections: Dict[str, Set[WebSocket]] = {}


async def broadcast_run_event(run_id: str, event: Event):
    """Broadcast an event to all connected WebSocket clients for a run."""
    if run_id not in connections:
        return
    disconnected = set()
    for ws in connections[run_id]:
        try:
            await ws.send_text(event.to_json())
        except Exception:
            disconnected.add(ws)
    connections[run_id] -= disconnected


@ws_router.websocket("/ws/runs/{run_id}")
async def run_events_websocket(websocket: WebSocket, run_id: str):
    await websocket.accept()

    # Register connection
    if run_id not in connections:
        connections[run_id] = set()
    connections[run_id].add(websocket)

    # Subscribe to event bus
    bus = EventBusManager.get_bus(run_id)

    def on_event(event: Event):
        asyncio.create_task(safe_send(websocket, event))

    bus.subscribe(on_event)

    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "run_id": run_id,
        "message": "WebSocket connected for run events",
        "timestamp": Event(run_id=run_id, type="connected").timestamp,
    })

    # Replay recent events from buffer
    buffered = bus.get_buffered_events()
    if buffered:
        await websocket.send_json({
            "type": "replay",
            "run_id": run_id,
            "events": [e.to_dict() for e in buffered[-50:]],
            "count": len(buffered[-50:]),
        })

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "replay":
                    # Replay events from database
                    since = msg.get("since")
                    events = await replay_events(run_id, since)
                    await websocket.send_json({
                        "type": "replay",
                        "run_id": run_id,
                        "events": events,
                        "count": len(events),
                    })

                elif msg_type == "subscribe":
                    # Already subscribed on connect
                    await websocket.send_json({
                        "type": "subscribed",
                        "run_id": run_id,
                    })

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        bus.unsubscribe(on_event)
        if run_id in connections:
            connections[run_id].discard(websocket)
            if not connections[run_id]:
                del connections[run_id]


async def safe_send(websocket: WebSocket, event: Event):
    try:
        await websocket.send_text(event.to_json())
    except Exception:
        pass
