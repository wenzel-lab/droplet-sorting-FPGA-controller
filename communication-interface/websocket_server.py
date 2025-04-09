import json
import asyncio
import os
import threading
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

import ast
import csv

from registers_management import write_register

# Path to the bias_values file
bias_file = os.path.join(os.path.dirname(__file__), '..', 'bias_values.tsv')
bias_file = os.path.abspath(bias_file)

# List of connected WebSocket clients
connected_clients = []

# -------------------- Fast API Setup -------------------------------------- #

# FastAPI instance
app = FastAPI()

# Model for POST requests to set register values
class RegisterRequest(BaseModel):
    offset: str         # Offset in hexadecimal format
    value: int          # Value in decimal format
    signed: bool        # Indicates if the value is signed

# Model for POST requests to set gain values
class GainRequest(BaseModel):
    values: list        # List of gain values to be written


@app.post("/register")
async def set_register(request: RegisterRequest):
    """
    Writes a value to a register given an offset.
    
    Args:
        request (RegisterRequest): Contains the offset, value, and signed flag.

    Returns:
        JSONResponse: A response indicating success or failure.
    """

    try:
        # Convert the hexadecimal offset to an integer
        offset_int = int(request.offset, 16)
        # Write the value to the register using the provided parameters
        write_register(offset_int, request.value, request.signed)
        return JSONResponse(content={"message": "Registro actualizado con éxito"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/setgain")
async def set_gain(request: GainRequest):
     """
    Sets the gain values and saves them in a .tsv file.
    
    Args:
        request (GainRequest): Contains a list of gain values to save.

    Returns:
        None: No return value.
    """

    try:
        # Save the gain values to the bias_values.tsv file
        with open(bias_file, "w", newline="") as file:
            writer = csv.writer(file, delimiter='\t')
            data = []
            # Prepare the data in rows of index and corresponding value
            for i in range(len(request.values)):
                data.append([i+1, request.values[i]])
            # Write the rows to the file
            writer.writerows(data)
    except Exception as e:
        print(f"Error while saving gain values: {e}")

@app.get("/download")
async def download_file():
    """
    Downloads the 'registers_data.txt' file.

    Returns:
        FileResponse: The response containing the file to download.
    """

    file_path = "registers_data.txt"  # Nombre fijo del archivo
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    try:
        # Serve the file as a download
        response = FileResponse(file_path, media_type="application/octet-stream", filename="registers_data.txt")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")


# WebSocket endpoint for streaming data
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming register and voltage data to clients.
    
    This WebSocket connection streams data from the 'registers_data.txt' and 'voltage_data.json' files
    to all connected clients at a regular interval. It ensures that all clients receive the latest data.

    Args:
        websocket (WebSocket): The WebSocket connection for the client.
    
    Returns:
        None: This function runs indefinitely, sending data to clients.
    """

    await websocket.accept()
    # Add the client to the list of connected clients
    connected_clients.append(websocket)
    print(f"Cliente conectado: {websocket.client}")
    try:
       while True:
        if os.path.exists("registers_data.txt"):
            with open("registers_data.txt", "r") as file:
                lineas = file.readlines()
                if lineas:
                    # Read the last line from the registers data
                    last_data = ast.literal_eval(lineas[-1].strip())
                if os.path.exists("voltage_data.json"):
                    with open("voltage_data.json", "r", encoding="utf-8") as file:
                        # Add the voltage history to the last register data
                        last_data["voltage_history"] = json.load(file)
                        # Serialize the combined data into a JSON message
                        message = json.dumps(last_data)
                        # Send the data to all connected clients
                        for client in connected_clients:
                            await client.send_text(message)
        # Wait for the next transmission interval (150ms)
        await asyncio.sleep(0.15) 
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        connected_clients.remove(websocket)

# Start the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
