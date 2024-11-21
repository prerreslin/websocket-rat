from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Ждем сообщения от клиента
            print(f"Получено: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Клиент отключился")

class Command(BaseModel):
    command: str

@app.post("/send-command/")
async def send_command(cmd: Command):
    if not cmd.command:
        raise HTTPException(status_code=400, detail="Command is required")
    print(f"Получена команда: {cmd.command}")
    return {"status": "success", "command": cmd.command}