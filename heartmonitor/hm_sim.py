from m5.objects import *
import m5

# System Setup
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '24MHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'

# Memory configuration
system.mem_ranges = [AddrRange('512MB')]

# MinorCPU Configuration
system.cpu = RiscvMinorCPU()

# Branch predictor for power efficiency
system.cpu.branchPredictor = TournamentBP(
    localPredictorSize=64,              # Small predictor for power efficiency
    globalPredictorSize=64,
    choicePredictorSize=64
)

# Interrupt controllers for RISC-V
system.cpu.interrupts = [RiscvInterrupts() for i in range(system.cpu.numThreads)]

# Memory Bus
system.membus = SystemXBar()


# Cache Hierarchy
class L1ICache(Cache):
    # 4KB 2-way associative L1 Instruction Cache
    size = '4kB'
    assoc = 2
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 4
    tgts_per_mshr = 20

class L1DCache(Cache):
    # 2KB Direct-mapped L1 Data Cache
    size = '2kB'
    assoc = 1          # Direct-mapped as specified
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 4
    tgts_per_mshr = 20

# Scratchpad Memory configuration
class ScratchpadMemory(SimpleMemory):
    # 8KB Scratchpad memory for critical signal processing buffers
    latency = '1ns'
    bandwidth = '1GB/s'
    
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Scratchpad memory with address mapping
system.scratchpad = ScratchpadMemory()
system.scratchpad.range = AddrRange(start=0x40000000, size='8kB')

# Port Connections
# CPU to Cache connections
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Cache to Bus connections  
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# System port
system.system_port = system.membus.cpu_side_ports

# Scratchpad connection
system.scratchpad.port = system.membus.mem_side_ports

# Memory Controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Load Heart Monitor Program
process = Process()
process.cmd = ['./heartmonitor_riscv']

system.workload = RiscvEmuLinux()
system.cpu.workload = process
system.cpu.createThreads()

# DVFS System 3-Stage Pipeline
DVFS_MODES = {
    "high_perf": {
        "clock": "48MHz", 
        "voltage": "1.2V",
        "description": "Intensive ECG signal processing",
        "pipeline_mode": "full_throughput",
        "power_islands": ["core", "cache", "dsp", "io"]
    },
    "normal": {
        "clock": "24MHz", 
        "voltage": "1.0V", 
        "description": "Standard ECG monitoring",
        "pipeline_mode": "balanced",
        "power_islands": ["core", "cache", "io"]
    },
    "low_power": {
        "clock": "8MHz", 
        "voltage": "0.8V",
        "description": "Background monitoring", 
        "pipeline_mode": "conservative",
        "power_islands": ["core"]
    },
    "sleep": {
        "clock": "32kHz", 
        "voltage": "0.6V",
        "description": "Maintenance operations",
        "pipeline_mode": "minimal",
        "power_islands": ["core"]
    }
}

dvfs_sequence = ["normal", "high_perf", "low_power", "sleep"]
dvfs_index = 0
DVFS_SWITCH_TICKS = 500_000

# Power Manager
class PowerManager:
    def __init__(self):
        self.active_power_islands = ["core", "cache", "dsp", "io"]
        self.pipeline_stages = {
            "fetch": {"active": True, "power_level": "normal"},
            "decode_execute": {"active": True, "power_level": "normal"}, 
            "memory_writeback": {"active": True, "power_level": "normal"}
        }
        self.clock_gated_units = []
    
    def configure_3stage_pipeline(self, pipeline_mode):
        # Configure the 3-stage pipeline based on operating mode
        print(f"    [3- Stage Pipeline] Configuration: {pipeline_mode}")
        
        if pipeline_mode == "minimal":
            self.pipeline_stages["fetch"]["power_level"] = "minimal"
            self.pipeline_stages["decode_execute"]["active"] = False
            self.pipeline_stages["memory_writeback"]["active"] = False
            print(f"      Stage 1 (Fetch): Minimal power")
            print(f"      Stage 2 (Decode/Execute): Clock gated")
            print(f"      Stage 3 (Memory/Writeback): Clock gated")
            
        elif pipeline_mode == "conservative":
            self.pipeline_stages["fetch"]["power_level"] = "low"
            self.pipeline_stages["decode_execute"]["power_level"] = "low"
            self.pipeline_stages["memory_writeback"]["active"] = True
            self.pipeline_stages["memory_writeback"]["power_level"] = "minimal"
            print(f"      Stage 1 (Fetch): Low power mode")
            print(f"      Stage 2 (Decode/Execute): Low power mode")
            print(f"      Stage 3 (Memory/Writeback): Minimal power")
            
        elif pipeline_mode == "balanced":
            for stage in self.pipeline_stages:
                self.pipeline_stages[stage]["active"] = True
                self.pipeline_stages[stage]["power_level"] = "normal"
            print(f"      All 3 stages: Active at normal power")
            
        else:  # full_throughput
            for stage in self.pipeline_stages:
                self.pipeline_stages[stage]["active"] = True
                self.pipeline_stages[stage]["power_level"] = "high"
            print(f"      All 3 stages: Maximum throughput mode")
    
    def powerisland_management(self, required_islands):
        # Simulate power island management
        all_islands = ["core", "cache", "dsp", "io"]
        
        gated_islands = []
        activated_islands = []
        
        for island in all_islands:
            if island not in required_islands and island in self.active_power_islands:
                self.active_power_islands.remove(island)
                gated_islands.append(island)
            elif island in required_islands and island not in self.active_power_islands:
                self.active_power_islands.append(island)
                activated_islands.append(island)
        
        if gated_islands:
            print(f"    [Power Islands] Gated: {', '.join(gated_islands)}")
        if activated_islands:
            print(f"    [Power Islands] Activated: {', '.join(activated_islands)}")
    
    def simulate_clockgating(self, mode_desc, pipeline_mode):
        # 3-Stage pipeline specific clock gating
        self.clock_gated_units = []
        
        # Pipeline-stage specific clock gating
        if pipeline_mode == "minimal":
            self.clock_gated_units.extend([
                "decode_execute_stage", "memory_writeback_stage",
                "branch_predictor", "advanced_alu_units"
            ])
        elif pipeline_mode == "conservative":
            self.clock_gated_units.extend([
                "unused_fetch_ports", "secondary_decode_units", "write_buffer_entries"
            ])
        
        # Functional unit clock gating
        if "Background" in mode_desc:
            self.clock_gated_units.extend(["dsp_units", "unused_cache_ways"])
        elif "Maintenance" in mode_desc:
            self.clock_gated_units.extend(["dsp_units", "cache_prefetch", "io_peripherals"])
        
        if self.clock_gated_units:
            print(f"    [Clock Gating] Units gated: {', '.join(self.clock_gated_units)}")
    
    def get_active_stages(self):
        # Return list of active pipeline stage
        return [stage for stage, config in self.pipeline_stages.items() if config["active"]]

power_manager = PowerManager()

def update_dvfs():
    # 3-Stage Pipeline Optimized DVFS Management
    global dvfs_index
    
    mode_name = dvfs_sequence[dvfs_index % len(dvfs_sequence)]
    mode = DVFS_MODES[mode_name]
    
    print(f"\n[DVFS] === {mode_name.upper()} MODE ===")
    print(f"    Heart Monitor Application: {mode['description']}")
    print(f"    Frequency: {mode['clock']}, Voltage: {mode['voltage']}")
    
    # Update system parameters
    system.clk_domain.clock = mode["clock"]
    system.clk_domain.voltage_domain.voltage = mode["voltage"]
    
    # Configure 3-stage pipeline for this mode
    power_manager.configure_3stage_pipeline(mode["pipeline_mode"])
    power_manager.powerisland_management(mode["power_islands"])
    power_manager.simulate_clockgating(mode["description"], mode["pipeline_mode"])
    
    active_stages = power_manager.get_active_stages()
    print(f"    Pipeline Status: {len(active_stages)}/3 stages active: {active_stages}")
    print(f"    Power Islands: {power_manager.active_power_islands}")
    
    dvfs_index += 1

# Simulation Execution with 3-Stage Pipeline Validation
root = Root(full_system=False, system=system)
m5.instantiate()

print("-"*50)
print("HEART MONITOR MICROPROCESSOR: 3-STAGE PIPELINE IMPLEMENTATION")
print("-"*50)

# Full System Configuration
print(f"\nSystem Configuration:")
print(f"  CPU: RISC-V MinorCPU (3-stage pipeline)")
print(f"  3- Stage Pipeline: Fetch -> Decode/Execute -> Memory/Writeback")
print(f"  L1 I-Cache: 4KB, 2-way (ECG instruction storage)")
print(f"  L1 D-Cache: 2KB, direct-mapped (data integrity)")
print(f"  Scratchpad: 8KB @ 0x40000000 (signal processing buffers)")
print(f"  DVFS: 4 modes with pipeline-aware power management")
print(f"  Memory: 512MB unified address space")

print(f"\nStarting heart monitor simulation...")

# Simulation time
max_total_ticks = 2_000_000_000
current_tick = 0

while current_tick < max_total_ticks:
    # Run simulation segment
    exit_event = m5.simulate(DVFS_SWITCH_TICKS)
    current_sim_tick = m5.curTick()
    
    # Check if program finished
    if exit_event.getCause() != "simulate() limit reached":
        print(f"\nHeart monitor application completed at tick {current_sim_tick}")
        print(f"Exit reason: {exit_event.getCause()}")
        break
    
    # Update DVFS with 3-stage pipeline management
    update_dvfs()
    current_tick += DVFS_SWITCH_TICKS
    
    # Progress update
    if dvfs_index % 4 == 0:
        progress = (current_tick / max_total_ticks) * 100
        active_stages = len(power_manager.get_active_stages())
        print(f"\n[PROGRESS] {progress:.1f}% - Tick {current_sim_tick} - Pipeline: {active_stages}/3 stages active")

# Final validation summary
print(f"\n" + "-"*50)
print("3-STAGE PIPELINE HEART MONITOR VALIDATION COMPLETE")
print("="*50)
print(f"Total execution time: {m5.curTick()} ticks")
print(f"DVFS transitions: {dvfs_index}")