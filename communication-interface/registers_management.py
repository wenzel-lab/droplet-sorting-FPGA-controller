import mmap
import struct

MEMORY_ADDRESS = 0x40600000     # Base memory address for register
MEMORY_SIZE = 0x20000           # Total memory size to map
STREAM_REGISTER_SIZE = 4        # Size of each register in bytes


def write_register(offset, value, signed):

"""
Writes a value to a register at a given offset in memory.

Args:
    offset (int): Offset from the base memory address.
    value (int): Value to write.
    signed (bool): If True, write as signed int. If False, write as unsigned.

Raises:
    RuntimeError: If any error occurs during memory access or writing.
"""

    try:
        # Open /dev/mem to access physical memory
        with open("/dev/mem", "r+b") as f:
            # Create a memory-mapped object with the specified size and offset
            mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)

            # Move to the specific register offset
            mem.seek(offset)

            # Write the value as signed or unsigned integer
            if signed:
                mem.write(struct.pack('i', value))
            else:
                mem.write(struct.pack('I', value))
            mem.close()
    except Exception as e:
        # Raise a runtime error with context if something fails
        raise RuntimeError(f"Error writing to register at offset {offset}: {e}")