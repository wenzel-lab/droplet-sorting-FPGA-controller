import time
import sched
import json

from registers_management import read_register, write_register
from voltage_conversion import analog_voltage

# Leer el archivo JSON
with open('config.json', 'r') as file:
    vars_data = json.load(file)

vars_to_send = vars_data["variables_to_send"]

# Crear el scheduler
scheduler = sched.scheduler(time.time, time.sleep)

voltage_buffer = []
MAX_LEN_BUFFER = 20000

# Función de lectura programada
def scheduled_read(file):
    global last_droplet_id, voltage_buffer
    # Leer datos desde la memoria

    data = {var_name: read_register(int(var_info["addr"],16),var_info["signed"]) for var_name, var_info in vars_to_send.items()}
    data["analog_voltage"] = analog_voltage(data["raw_voltage"], vars_to_send["raw_voltage"]["signed"])
    
    if len(voltage_buffer)<20000:
        voltage_buffer.append(data["analog_voltage"])
    else:
        voltage_buffer = []

    current_droplet_id = data["droplet_id"]

    # Verificar si el valor ha cambiado
    if data["droplet_id"] != last_droplet_id:
        # Guardar el valor en el archivo cuando haya un cambio
        file.write(f"Change detected at {time.time()}: {current_droplet_id}, Voltage signal: {voltage_buffer}\n")
        file.flush()  # Asegurarse de que se guarde inmediatamente

        voltage_buffer = []
        last_droplet_id = current_droplet_id

        # Imprimir para depuración
        print(f"Change detected: {current_droplet_id}")

    # Reprogramar la lectura en el siguiente intervalo de tiempo
    scheduler.enter(1 / 1000, 1, scheduled_read, (file,))  # 100 kHz -> 10 microsegundos


with open('registro_cambios.txt', 'w') as file:

    # Inicializar el valor anterior
    last_droplet_id = None

    # Programar la primera lectura
    scheduler.enter(0, 1, scheduled_read, (file,))

    # Ejecutar el scheduler (comenzar el ciclo de lecturas)
    scheduler.run()