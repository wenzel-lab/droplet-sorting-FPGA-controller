import mmap
import struct

MEMORY_ADDRESS = 0x40600000  # Dirección base de memoria
MEMORY_SIZE = 0x20000       # Tamaño de memoria
STREAM_REGISTER_SIZE = 4       # Tamaño del registro (en bytes)

# Función para leer un registro
def read_register(off,signed):
    try:
        with open("/dev/mem", "r+b") as f:
            mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)
            mem.seek(off)
            if signed:
                value = int.from_bytes(mem.read(STREAM_REGISTER_SIZE), byteorder='little', signed=True)
            else:
                value = int.from_bytes(mem.read(STREAM_REGISTER_SIZE), byteorder='little', signed=False)
            mem.close()
        return value
    except Exception as e:
        print(f"Error reading register: {e}")

def write_register(offset, value):
    try:
        with open("/dev/mem", "r+b") as f:
            mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)
            mem.seek(offset)
            mem.write(struct.pack('I', value))
            mem.close()
    except Exception as e:
        raise RuntimeError(f"Error escribiendo en registro: {e}")