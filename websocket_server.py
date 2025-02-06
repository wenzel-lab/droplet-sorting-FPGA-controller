import json
import asyncio
import os
import threading
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

import ast

from registers_management import write_register
from voltage_conversion import analog_voltage

# Leer el archivo JSON
with open('config.json', 'r') as file:
    vars_data = json.load(file)

vars_to_send = vars_data["variables_to_send"]

# Lista de clientes WebSocket conectados
connected_clients = []

# -------------------- Fast Api -------------------------------------- #

app = FastAPI()

# Modelo para solicitudes POST
class RegisterRequest(BaseModel):
    offset: str  # Offset en formato hexadecimal
    value: int   # Valor en formato decimal

@app.post("/register")
async def set_register(request: RegisterRequest):
    """Escribe un valor en un registro dado un offset."""
    try:
        offset_int = int(request.offset, 16)
        write_register(offset_int, request.value)
        return JSONResponse(content={"message": "Registro actualizado con éxito"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/download")
async def download_file():
    file_path = "registro_cambios.txt"  # Nombre fijo del archivo
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    try:
        response = FileResponse(file_path, media_type="application/octet-stream", filename="registro_cambios.txt")
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")


# WebSocket para transmitir datos en streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"Cliente conectado: {websocket.client}")
    try:
       while True:
        if os.path.exists("registro_cambios.txt"):
            with open("registro_cambios.txt", "r") as file:
                lineas = file.readlines()
                if lineas:
                    last_data = ast.literal_eval(lineas[-1].strip())
                if os.path.exists("registro_voltaje.json"):
                    with open("registro_voltaje.json", "r", encoding="utf-8") as file:
                        last_data["voltage_history"] = json.load(file)
                        message = json.dumps(last_data)
                        for client in connected_clients:
                            await client.send_text(message)
        await asyncio.sleep(0.15)  # Intervalo de transmision de datos (150ms)
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        connected_clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)