import time
import json
import pickle
import mmap

MEMORY_ADDRESS = 0x40600000  # Dirección base de memoria
MEMORY_SIZE = 0x01100       # Tamaño de memoria
STREAM_REGISTER_SIZE = 4       # Tamaño del registro (en bytes)

from collections import deque


from registers_management_alvaro import read_register, write_register
from voltage_conversion import analog_voltage

# Leer el archivo JSON
with open('config.json', 'r') as file:
    vars_data = json.load(file)

vars_to_send = vars_data["variables_to_send"]

voltage_buffer = deque()
MAX_LEN_BUFFER = 20000
log_buffer = []  # Buffer para almacenar los logs

last_droplet_id = None

# Extraer direcciones y configuraciones para optimizar accesos
addr_droplet_id = int(vars_to_send["droplet_id"]["addr"], 16)
addr_raw_voltage = int(vars_to_send["raw_voltage"]["addr"], 16)
size = STREAM_REGISTER_SIZE
signed_droplet = vars_to_send["droplet_id"]["signed"]
signed_voltage = vars_to_send["raw_voltage"]["signed"]

# Calcular start_offset y end_offset basados en las direcciones en vars_to_send
addresses = [int(var_info["addr"], 16) for var_info in vars_to_send.values()]
start_offset = min(addresses)  # Dirección mínima
end_offset = max(addresses) + STREAM_REGISTER_SIZE  # Dirección máxima, ajustada para incluir el último registro

# Función para realizar las lecturas principales
def read_completo(mem, addr_droplet_id, addr_raw_voltage, size, signed_droplet, signed_voltage):
    global voltage_buffer, last_droplet_id


    # Leer registros principales
    #t1 = time.perf_counter()
    current_droplet_id = read_register_optimized(mem, addr_droplet_id, size, signed_droplet)
    voltage = read_register_optimized(mem, addr_raw_voltage, size, signed_voltage)
    #t2 = time.perf_counter()
    #print(f"Tiempo para leer current_droplet_id: {(t2 - t1) * 1_000_000:.3f} microsegundos")

    # Administrar buffer de voltaje
    if len(voltage_buffer) < 20000:
        voltage_buffer.append(voltage)
    else:
        voltage_buffer.clear()  # Reinicia buffer para evitar sobrecarga

        # Verificar si el valor ha cambiado
    if current_droplet_id != last_droplet_id:
        # Llamar a la función para leer todos los registros
        #t1 = time.perf_counter()
        data = read_all_registers_optimized(mem, vars_to_send)
        #t2 = time.perf_counter()
        #print(f"Tiempo para recopilar datos de registros: {(t2 - t1) * 1_000_000:.3f} microsegundos")
        
        last_droplet_id = current_droplet_id

        # Imprimir para depuración
        print(f"Change detected: {current_droplet_id}")

def read_all_registers_optimized(mem, vars_to_send):
    """
    Read multiple registers using read_register_optimized for each variable in vars_to_send.

    Parameters:
        mem (mmap.mmap): The memory-mapped object for /dev/mem.
        vars_to_send (dict): Dictionary of variable information, including addresses and signed status.

    Returns:
        dict: A dictionary of register names and their corresponding values.
    """
    data = {}
    try:
        for var_name, var_info in vars_to_send.items():
            # Extraemos la dirección y configuración de la variable
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
# Función para leer directamente un valor desde la memoria
def read_register_optimized(mem, offset, size, signed):
    """
    Optimized register read using slicing instead of `seek` and `read`.
    """
    try:
        value = int.from_bytes(mem[offset:offset + size], byteorder="little", signed=signed)
        return value
    except Exception as e:
        print(f"Error reading register: {e}")
        return None

# Función para realizar las lecturas principales
def read_fast(mem, addr_droplet_id, addr_raw_voltage, size, signed_droplet, signed_voltage):
    global voltage_buffer, last_droplet_id


    # Leer registros principales
    t1 = time.perf_counter()
    current_droplet_id = read_register_optimized(mem, addr_droplet_id, size, signed_droplet)
    voltage = read_register_optimized(mem, addr_raw_voltage, size, signed_voltage)
    t2 = time.perf_counter()
    print(f"Tiempo para leer current_droplet_id: {(t2 - t1) * 1_000_000:.3f} microsegundos")

    # Administrar buffer de voltaje
    if len(voltage_buffer) < 20000:
        voltage_buffer.append(voltage)
    else:
        voltage_buffer.clear()  # Reinicia buffer para evitar sobrecarga

    # Detectar cambios
    if current_droplet_id != last_droplet_id:
        # Read all registers
        t1 = time.perf_counter()
        data = {
            var_name: read_register(mem, int(var_info["addr"], 16), var_info["signed"])
            for var_name, var_info in vars_to_send.items()
        }
        t2 = time.perf_counter()
        print(f"Tiempo para recopilar datos de registros: {(t2 - t1) * 1_000_000:.3f} microsegundos")

        log_entry = f"Change detected at {time.time()}: {current_droplet_id}, Voltage: {voltage}\n"
        log_buffer.append(log_entry)
        voltage_buffer = deque()
        last_droplet_id = current_droplet_id


# Función de lectura programada
def read(mem):
    global voltage_buffer, last_droplet_id

    #start_time = time.perf_counter()

    t1 = time.perf_counter()
    current_droplet_id = read_register(mem, int(vars_to_send["droplet_id"]["addr"], 16), vars_to_send["droplet_id"]["signed"])
    t2 = time.perf_counter()
    print(f"Tiempo para leer current_droplet_id: {(t2 - t1) * 1_000_000:.3f} microsegundos")

    #t1 = time.perf_counter()
    voltage = read_register(mem, int(vars_to_send["raw_voltage"]["addr"], 16), vars_to_send["raw_voltage"]["signed"])
    #t2 = time.perf_counter()
    #print(f"Tiempo para leer raw_voltage: {(t2 - t1) * 1_000_000:.3f} microsegundos")

    #t1 = time.perf_counter()
    if len(voltage_buffer) < 20000:
        voltage_buffer.append(voltage)
    else:
        voltage_buffer = deque()
    #t2 = time.perf_counter()
    #print(f"Tiempo para manejar el buffer de voltaje: {(t2 - t1) * 1_000_000:.3f} microsegundos")

    #t1 = time.perf_counter()
    if current_droplet_id != last_droplet_id:
        # Read all registers
        t1 = time.perf_counter()
        data = {
            var_name: read_register(mem, int(var_info["addr"], 16), var_info["signed"])
            for var_name, var_info in vars_to_send.items()
        }
        t2 = time.perf_counter()
        print(f"Tiempo para recopilar datos de registros: {(t2 - t1) * 1_000_000:.3f} microsegundos")

        #t1 = time.perf_counter()
        data["analog_voltage"] = analog_voltage(data["raw_voltage"], vars_to_send["raw_voltage"]["signed"])
        #t2 = time.perf_counter()
        #print(f"Tiempo para calcular analog_voltage: {(t2 - t1) * 1_000_000:.3f} microsegundos")

        #t1 = time.perf_counter()
        # Write changes to file
        #with open('registro_cambios.txt', 'w') as file:
            #   file.write(f"Change detected at {time.time()}: {current_droplet_id}, Voltage signal: {voltage_buffer}\n")
            #  file.flush()
        # Accumulate changes to log later
        log_entry = f"Change detected at {time.time()}: {current_droplet_id}, Voltage signal: {voltage_buffer}\n"
        log_buffer.append(log_entry)
        #t2 = time.perf_counter()
        #print(f"Tiempo para escribir en el archivo: {(t2 - t1) * 1_000_000:.3f} microsegundos")

        #t1 = time.perf_counter()
        voltage_buffer = deque()
        last_droplet_id = current_droplet_id
        #t2 = time.perf_counter()
        #print(f"Tiempo para actualizar el buffer y ID: {(t2 - t1) * 1_000_000:.3f} microsegundos")

        # Debugging output
        print(f"Change detected: {current_droplet_id}")


    #end_time = time.perf_counter()
    #print(f"Tiempo total para ejecutar la función: {(end_time - start_time) * 1_000_000:.3f} microsegundos **************************")


# Inicializar memoria mapeada fuera del bucle
try:
    with open("/dev/mem", "r+b") as f:
        mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)

        # Bucle principal
        while True:
            #t1 = time.perf_counter()
            read_completo(mem, addr_droplet_id, addr_raw_voltage, size, signed_droplet, signed_voltage)
            #t2 = time.perf_counter()
            #print(f"Tiempo while: {(t2 - t1) * 1_000_000:.3f} microsegundos")

            # Escribir en el archivo en bloque para evitar latencias frecuentes
            if log_buffer:
                with open('registro_cambios.txt', 'a') as log_file:
                    log_file.writelines(log_buffer)
                log_buffer.clear()

except Exception as e:
    print(f"Error initializing memory mapping or during execution: {e}")

#while True:
    #t1 = time.perf_counter()
    #read(mem)
    #t2 = time.perf_counter()
    #print(f"Tiempo while: {(t2 - t1) * 1_000_000:.3f} microsegundos")




import pickle

# Guardar datos
data = {"name": "Constanza", "age": 30, "city": "Santiago"}
with open("data.pkl", "wb") as file:
    pickle.dump(data, file)

# Leer datos
with open("data.pkl", "rb") as file:
    loaded_data = pickle.load(file)
print(loaded_data)