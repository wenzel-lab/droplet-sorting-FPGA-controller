# Redpitaya Droplet Sorting System – Monitoring & Communication Interface

This repository branch contains the software running on the **Redpitaya processor (ARM-based Linux OS)**. It is **not** include the FPGA logic. Instead, it implements the communication interface and data handling for the Redpitaya system, based on a shared memory register map with the FPGA. It enables external control and monitoring of internal FPGA registers and system voltages via WebSocket and HTTP interfaces.

---

## Key Directories 

### communication-interface/

### rp-images/

The `rp-images` folder contains different versions of Redpitaya images that have been developed so far. These versions are backed up in case it is necessary to test a previous one, even though it is possible to generate new images using the resources available in the [Pyrpl repository](https://github.com/wenzel-lab/pyrpl/tree/updated-2025).  

The differences between each image lie in certain modifications made to the `red_pitaya_fads.sv` file, which is located in the Pyrpl repository mentioned above.


- `red_pitaya_uncompressed-updated-muxaddr.bit.bin`: The updated version (below) writing the `mux_addr_i` and `muxing_channels_o` variables to the memory space of redpitaya.
- `red_pitaya_uncompressed-updated-signal-duration.bit.bin`: The updated version (below) adding the `signal_duration` variable in `red_pitaya_fads.sv` file.
- `red_pitaya_uncompressed-updated-signed.bit.bin`: The updated version (below) considering as `signed` the voltages variables in `red_pitaya_fads.sv` file.
- `red_pitaya_uncompressed-updated.bit.bin`: Last version created from branch `open_fpga_fads` in [Pyrpl repository](https://github.com/wenzel-lab/pyrpl/tree/open_fpga_fads).  

To use a specific image on the Red Pitaya hardware, it must be placed in the `root/` directory and renamed to `red_pitaya_uncompressed.bit.bin`.

## Purpose

This implementation supports:

- Fast **monitoring of voltages and internal register values**
- File based **periodic logging** of voltages and register changes
- Remote **data acquisition and control** using a WebSocket connection and HTTP protocol

---

## System Architecture

The diagram below shows the architecture of the Redpitaya system, highlighting how the FPGA and processor interact through a shared memory and communication layers:

![System Diagram](image.png)


**Functional Components**:
- **FPGA Chip**: Implements the droplet detection and classification algorithm. It activates a digital I/O (DIO) pin when a pulse is detected.
- **Shared Memory Register Map**: Acts as the communication interface between the FPGA and the processor. Registers are periodically updated with voltage, bias, and classification data.
- **Redpitaya Processor Software**:
  - **Monitor Script**: Reads the register data and voltages, updates local memory, and periodically stores new values to files.
  - **Voltage Conversion Script**: Converts digital register values to analog voltages.
  - **Registers Management Script**: Writes values to the shared memory map.
  - **WebSocket and HTTP Server**:
    - WebSocket for real-time data transmission (registers and voltage history).
    - HTTP server to receive remote POST requests for parameter updates.
- **External Files**:
  - `registro_cambios.txt`: Tracks register change events.
  - `registro_voltaje.json`: Stores the last voltages per channel.
  - `bias_values.tsv`: Defines the bias voltages for each channel.
  - **Configuration File**: Maps each register to a human-readable variable name and metadata (see below).
- **External Boards**:
  - **Pulse Board**: Provides droplet signal via DIO input.
  - **Multiplexer Board**: Controlled via SPI from the processor for channel switching.

---

## Redpitaya Communication Interface Logic

## Register Variables Description

The system uses a configuration file to define each variable information, such as associated register address and data type. This ensures readable and scalable communication between scripts and hardware.

| Variable Name        | Register Address | Type    | Description                                      |
|----------------------|------------------|---------|--------------------------------------------------|
| `var_1`  | `0x01`           | `float` | Voltage measured on channel 1                    |


You can modify the configuration file to update or expand the set of handled variables. This file is received at the beginning of monitor.py execution, so if it is modified, the mentioned script must be restarted.

## Getting Started


## Remote Client


## Files Overview


## Development Notes