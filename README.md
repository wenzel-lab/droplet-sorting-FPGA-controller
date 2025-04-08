# Redpitaya Droplet Sorting System – Monitoring & Communication Interface

This repository branch contains the software running on the **Redpitaya processor (ARM-based Linux OS)**. It is **not** include the FPGA logic. Instead, it implements the communication interface and data handling for the Redpitaya system, based on a shared memory register map with the FPGA. It enables external control and monitoring of internal FPGA registers and system voltages via WebSocket and HTTP interfaces.

---

## Key Directories 

### rp-images/

The `rp-images` folder contains different versions of Redpitaya images that have been developed so far. These versions are backed up in case it is necessary to test a previous one, even though it is possible to generate new images using the resources available in the [Pyrpl repository](https://github.com/wenzel-lab/pyrpl/tree/updated-2025).  

The differences between each image lie in certain modifications made to the `red_pitaya_fads.sv` file, which is located in the Pyrpl repository mentioned above.


- `red_pitaya_uncompressed-updated-muxaddr.bit.bin`: The updated version (below) writing the `mux_addr_i` and `muxing_channels_o` variables to the memory space of redpitaya.
- `red_pitaya_uncompressed-updated-signal-duration.bit.bin`: The updated version (below) adding the `signal_duration` variable in `red_pitaya_fads.sv` file.
- `red_pitaya_uncompressed-updated-signed.bit.bin`: The updated version (below) considering as `signed` the voltages variables in `red_pitaya_fads.sv` file.
- `red_pitaya_uncompressed-updated.bit.bin`: Last version created from branch `open_fpga_fads` in [Pyrpl repository](https://github.com/wenzel-lab/pyrpl/tree/open_fpga_fads).  

To use a specific image on the Red Pitaya hardware, it must be placed in the `root/` directory and renamed to `red_pitaya_uncompressed.bit.bin`.

### communication-interface/

The `communication-interface` folder contains the files and scripts associated with the monitoring of the registers and voltages, and the implementation of the communication interface through a Websocket Server and HTTP protocol.

The documentation in this `README.md` refers mainly to the codes contained in this folder.

---

## Purpose

This implementation supports:

- Fast **monitoring of voltages and internal register values**
- File based **periodic logging** of voltages and register changes
- Remote **data acquisition and control** using a WebSocket connection and HTTP protocol

---

## System Architecture

The diagram below shows the architecture of the Redpitaya system, highlighting how the FPGA and processor interact through a shared memory and communication layers:

![System Diagram](docs/diagram.png)


**Functional Components**:
- **FPGA Chip**: Implements the droplet detection and classification algorithm. It interacts with the Pulse Board through a digital I/O (DIO) pin that is activated. It also writes to the registers and reads the variables stored in them.
- **Shared Memory Register Map**: Acts as the communication interface between the FPGA and the processor. 
- **Redpitaya Processor Software**:
  - **Monitor Script** (`monitor.py`): Reads the register data and voltages, updates local variables stored in RAM if certain specified conditions are met and, periodically, these local variables are stored in files: `registro_cambios.txt` and `registro_voltaje.json`.
  - **Voltage Conversion Script** (`voltage_conversion.py`): Converts digital register values to analog voltages.
  - **Registers Management Script** (`registers_management.py`): Implements a function to write values to the shared memory map.
  - **WebSocket and HTTP Server** (`websocket_server.py`):
    - WebSocket for continuous data transmission (last registers values and voltage signal fragment of each channel). The information to send is obtained from the files `registro_cambios.txt` and `registro_voltaje.json`.
    - HTTP server to receive remote POST requests for parameter updates and for sending the file with the historical values of the registers (`registro_cambios.txt`).
- **External Files**:
  - `registro_cambios.txt`: Stores the historical values of the registers.
  - `registro_voltaje.json`: Stores the last voltage signal fragment of each channel.
  - `bias_values.tsv`: Stores the bias voltages for each channel. These values are sent to the Multiplexer Board through SPI protocol.
  - **Configuration File** (`config.json`): File with the information of the registers and the variables associated with them.
- **External Boards**:
  - **Pulse Board**: Provides pulses for the Droplet Sorting System.
  - **Multiplexer Board**: Controlled via SPI from the processor for channel switching.

---

## Redpitaya Communication Interface Logic

## Register Variables Description

The system uses a configuration file to define each variable information, such as associated register address and data type. This ensures readable and scalable communication between scripts and hardware.

|Variable Name|Register Address|Size|FPGA Data Type|Converted Data Type|Description|
|-------------|----------------|----|--------------|-------------------|-----------|
|`min_intensity_thresh`| `0x01000` to `0x01014` | `6` | `int`| `float` (mapped to analog voltage range)| Noise (peak) threshold detector (1-6)|
|`low_intensity_thresh`| `0x01020` to `0x01034` | `6` | `int`| `float` (mapped to analog voltage range)| Lower peak intensity sorting threshold for droplets (1-6)|
|`high_intensity_thresh`| `0x01040` to `0x01054` | `6` | `int`| `float` (mapped to analog voltage range)| Maximum peak intensity sorting threshold for droplets (1-6)|
|`min_width_thresh`| `0x01060` to `0x01074` | `6` | `int`| `int` | Noise (width = hwfm) threshold detector (1-6)|
|`low_width_thresh`| `0x01080` to `0x01094` | `6` | `int`| `int` | Lower peak width sorting threshold for droplets (1-6)|
|`high_width_thresh`| `0x010a0` to `0x010b4` | `6` | `int`| `int`| Maximum peak width sorting threshold for droplets (1-6)|
|`min_area_thresh`| `0x010c0` to `0x010d4` | `6` | `int`| `float` (mapped to accumulated analog voltage range)| Noise AUC threshold detector (1-6)|
|`low_area_thresh`| `0x010e0` to `0x010f4` | `6` | `int`| `float` (mapped to accumulated analog voltage range)| Lower AUC sorting threshold for droplets (1-6)|
|`high_area_thresh`| `0x01100` to `0x01114` | `6` | `int`| `float` (mapped to accumulated analog voltage range)| Maximum AUC sorting threshold for droplets (1-6)|
|`fads_reset`| `0x20` | `1` | `int`| `int`| Signal to reset the experiment values and classifier loops|


You can modify the configuration file to update or expand the set of handled variables. This file is received at the beginning of monitor.py execution, so if it is modified, the mentioned script must be restarted.

## Getting Started


## Remote Client


## Development Notes