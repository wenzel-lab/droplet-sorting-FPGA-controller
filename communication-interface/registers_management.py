import mmap
import struct

MEMORY_ADDRESS = 0x40600000  # Dirección base de memoria
MEMORY_SIZE = 0x20000       # Tamaño de memoria
STREAM_REGISTER_SIZE = 4       # Tamaño del registro (en bytes)


def write_register(offset, value, signed):
    try:
        with open("/dev/mem", "r+b") as f:
            mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)
            mem.seek(offset)
            if signed:
                mem.write(struct.pack('i', value))
            else:
                mem.write(struct.pack('I', value))
            mem.close()
    except Exception as e:
        raise RuntimeError(f"Error escribiendo en registro: {e}")