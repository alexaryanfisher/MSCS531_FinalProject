#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

// Heart Monitor Simulation

int main() {
    printf("Heart Monitor Starting...\n");
    
    int heartrate = 75;  // BPM
    int samplecount = 0;
    int processingcycles = 0;
    
    // Simulate continuous heart monitoring
    while(1) {
        // Simulate ECG signal acquisition (250-1000Hz sampling)
        for(int i = 0; i < 1000; i++) {
            samplecount++;
            
            // Simulate signal processing workload
            volatile int signalvalue = (samplecount * 47) % 1024;
            volatile int filtered = signalvalue + (signalvalue >> 2);
            
            // Simulate different processing intensities
            if(samplecount % 10000 == 0) {
                // High-intensity DSP processing (FFT simulation)
                for(int j = 0; j < 5000; j++) {
                    volatile int complexcalc = (j * filtered) % 2048;
                }
                processingcycles++;
                printf("ECG Processing Cycle %d - Samples: %d\n", 
                       processingcycles, samplecount);
            }
            
            // Simulate real-time constraints
            if(samplecount % 100000 == 0) {
                printf("Heart Rate: %d BPM - Total Samples: %d\n", 
                       heartrate + (samplecount % 20) - 10, samplecount);
            }
            
            // Exit condition for simulation
            if(samplecount > 1000000) {
                printf("Heart Monitor Simulation Complete\n");
                return 0;
            }
        }
        
        // Pause to simulate real-time behavior
        usleep(1000);  // 1ms pause
    }
    
    return 0;
}
