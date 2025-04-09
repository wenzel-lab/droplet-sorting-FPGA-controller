import time
import json
import mmap
import os
import threading
from collections import deque

from voltage_conversion import analog_voltage, analog_accum_voltage
from registers_management import write_register

# Memory configuration for direct FPGA register access via /dev/mem
MEMORY_ADDRESS = 0x40600000  # Base address of the memory-mapped region
MEMORY_SIZE = 0x20000        # Total memory size to map
STREAM_REGISTER_SIZE = 4     # Size of each register in bytes

# Load configuration JSON which defines which variables to read
try:
    with open('/root/droplet-sorting-FPGA-controller/communication-interface/config.json', 'r') as file:
        vars_data = json.load(file)
    vars_to_send = vars_data["variables_to_send"]
except Exception as e:
    print(f"Failed to load config.json: {e}")
    vars_to_send = {}

# Buffers and logging setup
log_buffer = []                 # Buffer to temporarily store event logs
log_voltage = {}                # Dictionary to store temporarily voltage history
lock = threading.Lock()         # Lock to ensure safe concurrent access
flush_interval = 0.1            # Time interval for flushing logs (in seconds)
last_droplet_id = None          # Track changes in droplet detection ID
last_cycle_id = None            # Track changes in voltage cycle ID

# Preprocess some register addresses and metadata for fast access
try:
    addr_droplet_id = int(vars_to_send["droplet_id"]["addr"], 16)
    addr_cycle_id = int(vars_to_send["update_cycle"]["addr"], 16)
    addrs_cur_adc_data = [int(addr, 16) for addr in vars_to_send["cur_adc_data"]["addr"]]
    addr_signal_duration = int(vars_to_send["signal_duration"]["addr"], 16)
    addr_enabled_channels = int(vars_to_send["enabled_channels"]["addr"], 16)
    signed_droplet = vars_to_send["droplet_id"]["signed"]
    signed_cycle_id = vars_to_send["update_cycle"]["signed"]
    signed_voltage = vars_to_send["cur_adc_data"]["signed"]
    signed_signal_duration = vars_to_send["signal_duration"]["signed"]
    signed_enabled_channels = vars_to_send["enabled_channels"]["signed"]
except KeyError as e:
    print(f"Configuration error: missing key {e}")
    exit(1)

# Voltage reading setup
mux_freq = 100                                                      # Multiplexer frequency in KHz
time_voltage_ms = 50                                                # Time window (in milliseconds) to record voltages
# Set the signal duration register in the FPGA 
write_register(addr_signal_duration, time_voltage_ms, 0)         
channels = 6                                                        # Total number of input channels available
enabled_channels = "000011"                                         # Bitmask indicating which channels are active (CH1 and CH2 are enabled here)
# Count how many channels are currently active (i.e., how many bits are '1')
active_channels = sum(int(bit) for bit in enabled_channels)
# Update the FPGA register that controls which channels are enabled
write_register(addr_enabled_channels, int(enabled_channels,2), 0)
# Calculate the number of voltage samples to store: total samples = duration × frequency / active channels
voltage_points = (time_voltage_ms)*mux_freq/active_channels
voltage_buffer = deque(maxlen=int(voltage_points))                  # Ring buffer for voltage history


# Read a single register from memory
def read_register(mem, offset, size, signed):
    """
    Reads a value from a memory-mapped register.

    Args:
        mem (mmap.mmap): Memory-mapped object representing the register space.
        offset (int): Offset in bytes from the base memory address.
        size (int): Number of bytes to read.
        signed (bool): Whether the value should be interpreted as signed.
    
    Returns:
        int or None: The integer value read from memory, or None if an error occurs.
    """

    try:
        return int.from_bytes(mem[offset:offset + size], byteorder="little", signed=signed)
    except Exception as e:
        print(f"Error reading register: {e}")
        return None

# Read all configured variables from memory
def read_all_registers(mem, vars_to_send):
    """
    Reads all specified memory registers from the vars_to_send dictionary and converts their values according to the specified data type.
    
    Args:
        mem (mmap.mmap): The object representing the memory from which registers are read.
        vars_to_send (dict): A dictionary containing the variables to read, with the following structure:
            {
                "var_name": {
                    "addr": <register address in hexadecimal format (string) or list of addresses>,
                    "signed": <boolean indicating if the value is signed>,
                    "data_type": <data type to convert ("voltage", "accum_voltage", "bits")>,
                    "bits_size": <bit size for "bits" type>
                }
            }

    Returns:
        dict: A dictionary with the results of the register reads, where keys are the variable names
              and values are the read and converted data.
              If an error occurs while reading the registers, it returns None.
    """

    data = {}
    try:
        for var_name, var_info in vars_to_send.items():
            if isinstance(var_info["addr"],list):
                data[var_name] = []
                for addr in var_info["addr"]:
                    addr = int(addr, 16)
                    signed = var_info["signed"]
                    data_type = var_info["data_type"]
                    bits_size = var_info["bits_size"]

                    value = read_register(mem, addr, STREAM_REGISTER_SIZE, signed)
                    try:
                        if data_type=="voltage":
                            value = analog_voltage(value,signed)
                        elif data_type=="accum_voltage":
                            value = analog_accum_voltage(value,signed)
                        elif data_type=="bits":
                            value = f"{value:0{bits_size}b}"[-bits_size:]
                    except Exception as conv_err:
                        print(f"Conversion error for {var_name}: {conv_err}")
                    data[var_name].append(value)
            else:
                addr = int(var_info["addr"], 16)
                signed = var_info["signed"]
                data_type = var_info["data_type"]
                bits_size = var_info["bits_size"]

                value = read_register(mem, addr, STREAM_REGISTER_SIZE, signed)
                try:
                    if data_type=="voltage":
                        value = analog_voltage(value,signed)
                    elif data_type=="accum_voltage":
                        value = analog_accum_voltage(value,signed)
                    elif data_type=="bits":
                        value = f"{value:0{bits_size}b}"[-bits_size:]
                except Exception as conv_err:
                    print(f"Conversion error for {var_name}: {conv_err}")
                data[var_name] = value
        return data
    except Exception as e:
        print(f"Error reading all registers: {e}")
        return None

# Main function that continuously reads system state
def read(mem, size):
    """
    Reads key registers and voltages for all channels, processes the data, and logs droplet events.
    If a new droplet event is detected or there is a change in settings, it logs the event data.

    Args:
        mem (mmap.mmap): The object representing the memory from which registers and voltage data are read.
        size (int): The size of the data to be read from the registers.

    Returns:
        None: This function does not return any values, but updates the voltage buffer and logs events.
    """

    global log_voltage, log_buffer, voltage_buffer, last_droplet_id, last_cycle_id, time_voltage_ms, voltage_points, enabled_channels, active_channels
    
    flag_change = 0
    
    try:
        # Read key registers
        current_droplet_id = read_register_optimized(mem, addr_droplet_id, size, signed_droplet)
        current_cycle_id = read_register_optimized(mem, addr_cycle_id, size, signed_cycle_id)
        current_time_voltage_ms = read_register_optimized(mem, addr_signal_duration, size, signed_signal_duration)
        current_enabled_channels_int = read_register_optimized(mem, addr_enabled_channels, size, signed_enabled_channels)
        current_enabled_channels = f"{current_enabled_channels_int:0{6}b}"[-6:]

        # If signal duration or channel activation changed, reset buffer
        if (time_voltage_ms!=current_time_voltage_ms) or (enabled_channels!=current_enabled_channels):
            time_voltage_ms = current_time_voltage_ms
            enabled_channels = current_enabled_channels
            active_channels = sum(int(bit) for bit in enabled_channels)
            if active_channels!=0:
                voltage_points = (time_voltage_ms)*mux_freq/active_channels
            else:
                voltage_points = 0
            voltage_buffer = deque(maxlen=int(voltage_points))  # Historial de voltajes
            flag_change = 1

        # If one cycle of voltage acquisition is completed then read voltages for all channels and store values of active ones 
        if current_cycle_id != last_cycle_id:
            voltage_per_channel = [analog_voltage(read_register_optimized(mem, ch_voltage_addr, size, signed_voltage),signed_voltage) for ch_voltage_addr in addrs_cur_adc_data]
            voltage_active_channels = []
            for i in range(channels):
                if int(enabled_channels[channels-1-i]):
                    voltage_active_channels.append(voltage_per_channel[i])
            voltage_buffer.append(voltage_active_channels)
            last_cycle_id = current_cycle_id

        # If a new droplet event occurred or settings changed, log it
        if (current_droplet_id != last_droplet_id) or flag_change:
            data = read_all_registers(mem, vars_to_send)
            event_log = data
            with lock:
                log_buffer.append(event_log)
            last_droplet_id = current_droplet_id
    except Exception as e:
        print(f"Error in read function: {e}")

# Thread: convert voltage buffer to JSON structure
def save_voltage_log():
    """
    Saves the voltage history from the voltage buffer into the log_voltage dictionary when voltage buffer becomes full.
    This function runs in an infinite loop and continuously updates the log until interrupted.

    Args:
        None

    Returns:
        None: This function does not return any values but updates the log_voltage dictionary with the voltage history.
    """

    global voltage_buffer, log_voltage, voltage_points, active_channels

    while True:
        try:
            if len(voltage_buffer)==int(voltage_points):
                voltage_buffer_copy = list(voltage_buffer)
                vh_list = [[] for _ in range(active_channels)]
                for ch_voltages in voltage_buffer_copy:
                    if ch_voltages:
                        for i in range(active_channels):
                            vh_list[i].append(ch_voltages[i])
                list_counter=0
                for i in range(channels):
                    if int(enabled_channels[channels-1-i]):
                        log_voltage[f"voltage_history_{i+1}"] = vh_list[list_counter]
                        list_counter+=1
                voltage_buffer.clear()
        except Exception as e:
            print(f"Error in save_voltage_log: {e}")


# Thread: periodically write event logs to disk
def save_logs_periodically():
    """
    Saves event logs periodically to a file.
    This function runs in an infinite loop, periodically checking the log_buffer for entries. 

    Args:
        None

    Returns:
        None: This function does not return any values but periodically writes log entries to a file.
    """

    global log_buffer

    while True:
        try:
            time.sleep(flush_interval)  # Esperar antes de intentar guardar
            with lock:
                log_buffer_copy = log_buffer
                if log_buffer_copy:
                    with open('/root/droplet-sorting-FPGA-controller/communication-interface/registers_data.txt', 'a') as log_file:
                        for entry in log_buffer_copy:
                            log_file.write(json.dumps(entry) + '\n')
                    log_buffer.clear()
                    log_buffer_copy.clear()
        except Exception as e:
            print(f"Error saving event logs: {e}")


# Thread: periodically write voltage history to disk as JSON
def save_voltage_periodically():
   ():
    """
    Saves voltage logs periodically to a JSON file.
    This function runs in an infinite loop, periodically checking the log_voltage for voltage data.

    Args:
        None

    Returns:
        None: This function does not return any values but periodically writes voltage logs to a file.
    """

    global log_voltage

    while True:
        try:
            time.sleep(flush_interval)  # Esperar antes de intentar guardar
            temp_path = "/root/droplet-sorting-FPGA-controller/communication-interface/voltage_data.json.tmp"  # Archivo temporal
            log_voltage_copy = log_voltage
            if log_voltage_copy:
                with open(temp_path, "w", encoding="utf-8") as file:
                    json.dump(log_voltage_copy, file) 
                log_voltage.clear()
                log_voltage_copy.clear()
                os.replace(temp_path, "/root/droplet-sorting-FPGA-controller/communication-interface/voltage_data.json")
        except Exception as e:
            print(f"Error saving voltage log: {e}")


# Initialization and main execution loop
try:
    with open("/dev/mem", "r+b") as f:
        mem = mmap.mmap(f.fileno(), MEMORY_SIZE, offset=MEMORY_ADDRESS)

        # Clear the log file at startup
        try:
            with open('/root/droplet-sorting-FPGA-controller/communication-interface/registers_data.txt', 'w') as log_file:
                log_file.truncate(0) 
        except Exception as e:
            print(f"Could not clear log file: {e}")

        # Start logging threads
        threading.Thread(target=save_voltage_log, daemon=True).start()
        threading.Thread(target=save_logs_periodically, daemon=True).start()
        threading.Thread(target=save_voltage_periodically, daemon=True).start()

        # Main read loop
        while True:
            read(mem, STREAM_REGISTER_SIZE)


except Exception as e:
    print(f"Critical error initializing memory or during execution: {e}")
