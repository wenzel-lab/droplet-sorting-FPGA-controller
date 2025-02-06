import time
import json
import pickle
import mmap
import os
import threading
from collections import deque

from voltage_conversion import analog_voltage
from registers_management import write_register

MEMORY_ADDRESS = 0x40600000  # Dirección base de memoria
MEMORY_SIZE = 0x01100       # Tamaño de memoria
STREAM_REGISTER_SIZE = 4       # Tamaño del registro (en bytes)

# Leer el archivo JSON
with open('/root/python_codes/config.json', 'r') as file:
    vars_data = json.load(file)

vars_to_send = vars_data["variables_to_send"]

# Buffers y configuración

size = STREAM_REGISTER_SIZE

log_buffer = []  # Buffer para almacenar los logs de evento
log_voltage = {} # Logs de voltaje
lock = threading.Lock()  # Asegura acceso seguro al log_buffer
flush_interval = 0.1 #Intervalo para que los threads guarden datos en archivo (100ms)
last_droplet_id = None
last_cycle_id = None

# Extraer direcciones y configuraciones para optimizar accesos
addr_droplet_id = int(vars_to_send["droplet_id"]["addr"], 16)
addr_cycle_id = int(vars_to_send["update_cycle"]["addr"], 16)
addrs_cur_adc_data = [int(addr, 16) for addr in vars_to_send["adc_values"]["addr"]] # cur_adc_data
addr_signal_duration = int(vars_to_send["signal_duration"]["addr"], 16)
addr_enabled_channels = int(vars_to_send["enabled_channels"]["addr"], 16)
signed_droplet = vars_to_send["droplet_id"]["signed"]
signed_cycle_id = vars_to_send["update_cycle"]["signed"]
signed_voltage = vars_to_send["adc_values"]["signed"]
signed_signal_duration = vars_to_send["signal_duration"]["signed"]
signed_enabled_channels = vars_to_send["enabled_channels"]["signed"]

# Buffer voltage signal
mux_freq = 200 # Khz
time_voltage_ms = 100
write_register(addr_signal_duration, time_voltage_ms)
enabled_channels = 1
write_register(addr_enabled_channels, enabled_channels)
voltage_points = (time_voltage_ms)*mux_freq/enabled_channels
voltage_buffer = deque(maxlen=int(voltage_points))  # Historial de voltajes

# Definir timestamp_us como global fuera de cualquier función
timestamp_us = None

# Función para leer directamente un valor desde la memoria
def read_register_optimized(mem, offset, size, signed):
    try:
        return int.from_bytes(mem[offset:offset + size], byteorder="little", signed=signed)
    except Exception as e:
        print(f"Error reading register: {e}")
        return None

def read_all_registers_optimized(mem, vars_to_send):
    data = {}
    try:
        for var_name, var_info in vars_to_send.items():
            # Extraemos la dirección y configuración de la variable
            if isinstance(var_info["addr"],list):
                data[var_name] = []
                for addr in var_info["addr"]:
                    addr = int(addr, 16)
                    size = STREAM_REGISTER_SIZE
                    signed = var_info["signed"]

                    # Leemos el registro usando read_register_optimized
                    value = read_register_optimized(mem, addr, size, signed)
                    data[var_name].append(value)
            else:
                addr = int(var_info["addr"], 16)
                size = STREAM_REGISTER_SIZE
                signed = var_info["signed"]

                # Leemos el registro usando read_register_optimized
                value = read_register_optimized(mem, addr, size, signed)
                data[var_name] = value

        return data
    except Exception as e:
        print(f"Error reading all registers: {e}")
        return None

# Función para realizar las lecturas principales
def read_completo(mem, addr_droplet_id, addrs_cur_adc_data, size, signed_droplet, signed_voltage):
    global log_voltage, log_buffer, voltage_buffer, last_droplet_id, last_cycle_id, timestamp_us, time_voltage_ms, voltage_points, enabled_channels
    
    flag_change = 0
    # Leer registros principales
    current_droplet_id = read_register_optimized(mem, addr_droplet_id, size, signed_droplet)
    current_cycle_id = read_register_optimized(mem, addr_cycle_id, size, signed_droplet)
    current_time_voltage_ms = read_register_optimized(mem, addr_signal_duration, size, signed_signal_duration)
    current_enabled_channels = read_register_optimized(mem, addr_enabled_channels, size, signed_enabled_channels)

    if (time_voltage_ms!=current_time_voltage_ms) or (enabled_channels!=current_enabled_channels):
        time_voltage_ms = current_time_voltage_ms
        enabled_channels = current_enabled_channels
        voltage_points = (time_voltage_ms)*mux_freq/enabled_channels
        voltage_buffer = deque(maxlen=int(voltage_points))  # Historial de voltajes
        flag_change = 1

    #if current_cycle_id != last_cycle_id:
    voltage_per_channel = [analog_voltage(read_register_optimized(mem, ch_voltage_addr, size, signed_voltage),signed_voltage) for ch_voltage_addr in addrs_cur_adc_data]

    # Guardar en el buffer de voltajes
    voltage_buffer.append(voltage_per_channel)

        #last_cycle_id = current_cycle_id


    # Verificar si el valor ha cambiado
    if (current_droplet_id != last_droplet_id) or flag_change:
        # Llamar a la función para leer todos los registros
        data = read_all_registers_optimized(mem, vars_to_send)
        tiemp = time.time() * 1_000_000 - timestamp_us
        timestamp_us = time.time() * 1_000_000  # En microsegundos
       
        # Crear el registro del evento
        event_log = {
            "timestamp": tiemp,
            "droplet_id": current_droplet_id,
            "all_data": data
        }

        # Proteger acceso al log_buffer
        with lock:
            log_buffer.append(event_log)

        last_droplet_id = current_droplet_id

def save_voltage_log():
    global voltage_buffer, log_voltage, voltage_points
    """Thread worker para guardar logs de senales de voltaje en un diccionario."""
    while True:
        if len(voltage_buffer)==int(voltage_points):
            voltage_buffer_copy = list(voltage_buffer)
            vh1 = []
            vh2 = []
            vh3 = []
            vh4 = []
            vh5 = []
            vh6 = []
            for ch_voltages in voltage_buffer_copy:
                if ch_voltages:
                    vh1.append(ch_voltages[0])
                    vh2.append(ch_voltages[1])
                    vh3.append(ch_voltages[2])
                    vh4.append(ch_voltages[3])
                    vh5.append(ch_voltages[4])
                    vh6.append(ch_voltages[5])
            log_voltage = {
                "voltage_history_1": vh1,
                "voltage_history_2": vh2,
                "voltage_history_3": vh3,
                "voltage_history_4": vh4,
                "voltage_history_5": vh5,
                "voltage_history_6": vh6
            }


def save_logs_periodically():
    global log_buffer
    """Thread worker para guardar logs de eventos en un archivo."""
    while True:
        time.sleep(flush_interval)  # Esperar antes de intentar guardar
        with lock:
            if log_buffer:
                with open('/root/python_codes/registro_cambios.txt', 'a') as log_file:
                    for entry in log_buffer:
                        log_file.write(json.dumps(entry) + '\n')
                log_buffer.clear()

def save_voltage_periodically():
    """Thread worker para guardar logs de voltaje en un archivo."""
    while True:
        time.sleep(flush_interval)  # Esperar antes de intentar guardar
        temp_path = "/root/python_codes/registro_voltaje.json.tmp"  # Archivo temporal
        if log_voltage:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(log_voltage, file) 
            log_voltage.clear()
            os.replace(temp_path, "/root/python_codes/registro_voltaje.json")


# Inicializar memoria mapeada fuera del bucle
try:
    with open("/dev/mem", "r+b") as f:
        mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)
        # Vaciar el archivo (sobrescribe el contenido)
        with open('/root/python_codes/registro_cambios.txt', 'w') as log_file:
            log_file.truncate(0) 

        # Inicia el thread para guardar datos
        threading.Thread(target=save_voltage_log, daemon=True).start()
        threading.Thread(target=save_logs_periodically, daemon=True).start()
        threading.Thread(target=save_voltage_periodically, daemon=True).start()
        timestamp_us = time.time() * 1_000_000  # En microsegundos
        # Bucle principal
        while True:
            read_completo(mem, addr_droplet_id, addrs_cur_adc_data, size, signed_droplet, signed_voltage)


except Exception as e:
    print(f"Error initializing memory mapping or during execution: {e}")
