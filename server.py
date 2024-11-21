from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio

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
            data = await websocket.receive_text()
            print(f"Получено от клиента: {data}")
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
    
    # Рассылаем сообщение всем подключённым клиентам
    for client in connected_clients:
        try:
            await client.send_text(cmd.command)
        except Exception as e:
            print(f"Ошибка отправки: {e}")
    
    return {"status": "success", "command": cmd.command}
