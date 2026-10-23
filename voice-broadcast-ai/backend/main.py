from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from broadcast_state import broadcast_state
from command_parser import parse_voice_command
from command_router import BroadcastCommandError, execute_command
from models import CommandResponse, VoiceCommandRequest


app = FastAPI(title="AI Voice Broadcast Controller", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        disconnected: list[WebSocket] = []
        for websocket in self.connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(websocket)


manager = ConnectionManager()


@app.get("/api/status")
async def get_status() -> dict:
    return broadcast_state.to_dict()


@app.post("/api/voice-command", response_model=CommandResponse)
async def voice_command(request: VoiceCommandRequest) -> CommandResponse:
    try:
        command = parse_voice_command(request.text)

        if command.requires_confirmation and not request.confirmed:
            return CommandResponse(
                success=False,
                message=(
                    f"Confirmation required for {command.action.value}. "
                    "Please say confirm."
                ),
                command=command,
                state=broadcast_state.to_dict(),
                confirmation_required=True,
            )

        message = await execute_command(command)
        state = broadcast_state.to_dict()

        await manager.broadcast({
            "type": "broadcast_state",
            "message": message,
            "state": state,
        })

        return CommandResponse(
            success=True,
            message=message,
            command=command,
            state=state,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except BroadcastCommandError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    await websocket.send_json({
        "type": "broadcast_state",
        "message": "Dashboard connected.",
        "state": broadcast_state.to_dict(),
    })

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
