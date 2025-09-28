#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

// Heart Monitor Simulation

int main() {
    printf("Heart Monitor Starting...\n");
    
    int heart_rate = 75;  // BPM
    int sample_count = 0;
    int processing_cycles = 0;
    
    // Simulate continuous heart monitoring
    while(1) {
        // Simulate ECG signal acquisition (250-1000Hz sampling)
        for(int i = 0; i < 1000; i++) {
            sample_count++;
            
            // Simulate signal processing workload
            volatile int signal_value = (sample_count * 47) % 1024;
            volatile int filtered = signal_value + (signal_value >> 2);
            
            // Simulate different processing intensities
            if(sample_count % 10000 == 0) {
                // High-intensity DSP processing (FFT simulation)
                for(int j = 0; j < 5000; j++) {
                    volatile int complex_calc = (j * filtered) % 2048;
                }
                processing_cycles++;
                printf("ECG Processing Cycle %d - Samples: %d\n", 
                       processing_cycles, sample_count);
            }
            
            // Simulate real-time constraints
            if(sample_count % 100000 == 0) {
                printf("Heart Rate: %d BPM - Total Samples: %d\n", 
                       heart_rate + (sample_count % 20) - 10, sample_count);
            }
            
            // Exit condition for simulation
            if(sample_count > 1000000) {
                printf("Heart Monitor Simulation Complete\n");
                return 0;
            }
        }
        
        // Pause to simulate real-time behavior
        usleep(1000);  // 1ms pause
    }
    
    return 0;
}