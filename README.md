# Heart Monitor Microprocessor Implementation with gem5 simulator

This repository contains the implementation project for MSCS531. It is the implementation of a low-power microprocessor design for wearable heart monitoring devices, simulated using gem5. 

# Project Overview
The project implements a 3-stage pipeline RISC-V processor with advanced power management features including DVFS, power gating, and clock gating optimized for ECG signal processing.

## Key Architectural Features
* ISA: RISCV with MinorCPU
* Pipeline: 3 Stage Design ( Fetch, Decode/Execute, Memory/Writeback)
* Clock Frequency: Adaptive 32kHz to 48MHz based on workload
* Power Management: 4-mode DVFS with power island control

## Memory Heirarchy
- L1 ICache: 4KB, 2 way associative
- L1 DCache: 2KB, direct mapped
- Scratchpad Memory: 8KB high speed buffer for signal processing
- Main Memory: 512MB DDR3

## Power Management System
- DVFS Modes: High Performance - 48MHz, 1.2V, Normal - 24MHz, 1.0V, Low Power - 8MHz, 0.8V, Sleep - 32kHz, 0.6V
- Power Islands: Core, Cache, DSP, I/O islands independent control
- Clock Gating: fine-gating of unused pipeline stages and functional units

# How to Run

1. Install Prerequistes (Shown below)
2. Clone and set up gem5
3. Clone this repository
4. Compile heart monitor application:

    ```
    riscv64-linux-gnu-gcc -static -o heartmonitor_riscv heartmonitor.c
    chmod +x heartmonitor_riscv 
   ```
5. Run simulation:

    `/path/to/gem5/build/RISCV/gem5.opt hm_sim.py`

### Prerequistes
```
# System dependencies and cross compiler
sudo apt-get update
sudo apt-get install build-essential get m4 scons python3-venv python3-dev python3-six wget curl protobuf-compiler gcc gcc-riscv64-linux-gnu g++-riscv-linux-gnu pkg-config python3-pip pip

# virtual environment and dependencies
python3 -m venv gem5_venv
# activate venv
source gem5_venv/bin/activate
pip install scons six pydot pydotplus
```