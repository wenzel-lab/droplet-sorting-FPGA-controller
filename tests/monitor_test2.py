import time
import json
import pickle

from collections import deque


from registers_management import read_register, write_register
from voltage_conversion import analog_voltage

# Leer el archivo JSON
with open('config.json', 'r') as file:
    vars_data = json.load(file)

vars_to_send = vars_data["variables_to_send"]

voltage_buffer = deque()
MAX_LEN_BUFFER = 20000

last_droplet_id = None

# Función de lectura programada
def read():
    global voltage_buffer, last_droplet_id

    current_droplet_id = read_register(int(vars_to_send["droplet_id"]["addr"],16),vars_to_send["droplet_id"]["signed"])
    voltage = read_register(int(vars_to_send["raw_voltage"]["addr"],16),vars_to_send["raw_voltage"]["signed"])

    if len(voltage_buffer)<20000:
        voltage_buffer.append(voltage)
    else:
        voltage_buffer = deque()

    # Verificar si el valor ha cambiado
    if current_droplet_id != last_droplet_id:
        data = {var_name: read_register(int(var_info["addr"],16),var_info["signed"]) for var_name, var_info in vars_to_send.items()}
        data["analog_voltage"] = analog_voltage(data["raw_voltage"], vars_to_send["raw_voltage"]["signed"])
    
        # Guardar el valor en el archivo cuando haya un cambio
        with open('registro_cambios.txt', 'w') as file:
            file.write(f"Change detected at {time.time()}: {current_droplet_id}, Voltage signal: {voltage_buffer}\n")
            file.flush()  # Asegurarse de que se guarde inmediatamente

        voltage_buffer = deque()
        last_droplet_id = current_droplet_id

        # Imprimir para depuración
        print(f"Change detected: {current_droplet_id}")


while True:
    #t1 = time.perf_counter()
    read()
    #t2 = time.perf_counter()
    #print(f"Tiempo para actualizar el buffer y ID: {(t2 - t1) * 1_000_000:.3f} microsegundos")



import pickle

# Guardar datos
data = {"name": "Constanza", "age": 30, "city": "Santiago"}
with open("data.pkl", "wb") as file:
    pickle.dump(data, file)

# Leer datos
with open("data.pkl", "rb") as file:
    loaded_data = pickle.load(file)
print(loaded_data)