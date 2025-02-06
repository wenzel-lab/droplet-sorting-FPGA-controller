import mmap
import struct

MEMORY_ADDRESS = 0x40600000  # Dirección base de memoria
MEMORY_SIZE = 0x01100       # Tamaño de memoria
STREAM_REGISTER_SIZE = 4       # Tamaño del registro (en bytes)

# Función para leer un registro
def read_register(mem, off, signed):
    """
    Read a specific register from the given memory mapping.

    Parameters:
        mem (mmap.mmap): The memory-mapped object for /dev/mem.
        off (int): The offset of the register to read.
        signed (bool): Whether the register is signed or unsigned.

    Returns:
        int: The value read from the register.
    """
    try:
        mem.seek(off)
        return int.from_bytes(mem.read(STREAM_REGISTER_SIZE), byteorder="little", signed=signed)
    except Exception as e:
        print(f"Error reading register: {e}")
        return None

# Función optimizada para leer múltiples registros de una vez
def read_all_registers(mem, vars_to_send, register_size):
    """
    Optimized function to read multiple registers from memory in a single batch operation.

    Parameters:
        mem (mmap.mmap): Memory-mapped object.
        vars_to_send (dict): Dictionary with variable information including addresses and signed settings.
        register_size (int): The size of each register in bytes.

    Returns:
        dict: Dictionary with variable names as keys and their read values as values.
    """
    try:
        # Determinar el rango mínimo y máximo a leer de memoria
        addresses = [int(var_info["addr"], 16) for var_info in vars_to_send.values()]
        start = min(addresses)
        end = max(addresses) + register_size

        # Leer el rango completo de memoria
        raw_data = mem[start:end]

        # Extraer los valores desde los datos leídos
        data = {}
        for var_name, var_info in vars_to_send.items():
            offset = int(var_info["addr"], 16) - start
            data[var_name] = int.from_bytes(
                raw_data[offset:offset + register_size],
                byteorder="little",
                signed=var_info["signed"]
            )
        return data

    except Exception as e:
        print(f"Error reading all registers: {e}")
        return {}
def write_register(offset, value):
    try:
        with open("/dev/mem", "r+b") as f:
            mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)
            mem.seek(offset)
            mem.write(struct.pack('I', value))
            mem.close()
    except Exception as e:
        raise RuntimeError(f"Error escribiendo en registro: {e}")