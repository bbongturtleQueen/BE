from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()

rooms = {}

@ws_router.websocket("/ws/{room_id}")
async def classroom_ws(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = []

    try:
        data = await websocket.receive_json()
        kid = data["userId"]

        rooms[room_id].append({"socket": websocket, "kid": kid})

        await broadcast(room_id, {
            "type": "join",
            "kid": kid,
            "list": [c["kid"] for c in rooms[room_id]]
        })

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        rooms[room_id] = [
            c for c in rooms[room_id] if c["socket"] != websocket
        ]

async def broadcast(room_id, message):
    for client in rooms[room_id]:
        await client["socket"].send_json(message)