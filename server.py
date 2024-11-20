from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from uvicorn import run

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Получено сообщение от клиента: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Клиент отключён")

@app.post("/send-command/")
async def send_command(command: str):
    """
    API для отправки команд всем подключённым клиентам.
    """
    await manager.broadcast(command)
    return {"message": f"Команда '{command}' отправлена всем подключённым клиентам"}

if __name__ == "__main__":
    run(app=app,port=5000)
