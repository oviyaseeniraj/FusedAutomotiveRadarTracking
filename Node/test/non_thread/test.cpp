// g++ -std=c++11 -Wall -Wextra -pedantic -lfftw3f -lm -I../../src/ -o test test.cpp `pkg-config --cflags --libs opencv4`; ./test 
#include "DataAcquisition.h"
#include "RangeDoppler.h"
#include "Visualizer.h"

#define INPUT_SIZE 64 * 512
#define OUTPUT_SIZE 0
int main(int argc, char* argv[])
{   

    // CONSTRUCTOR INITIATION
    DataAcquisition daq;

    RangeDoppler rdm("blackman");

    Visualizer vis(INPUT_SIZE,OUTPUT_SIZE);

    // BUFFER POINTER INITIATION
    uint16_t *in_bufferptr    = daq.getBufferPointer();
    float    *in_visualizeptr = rdm.getBufferPointer();
    float    *ang_visualizeptr = rdm.getAngleBufferPointer();
    int      *angidx_visptr = rdm.getAngleIndexPointer();
    float    *range_visualizeptr = rdm.getRangeBufferPointer();
    // this isn't used in what appears to be thier most recent test
    // can add to RadarBlock if needed eventually 
    // float    *angleMap_ptr = rdm.getAngleMapPointer();
    
    rdm.setBufferPointer(in_bufferptr);
    vis.setBufferPointer(in_visualizeptr);
    vis.setAngleBufferPointer(ang_visualizeptr);
    vis.setAngleIndexPointer(angidx_visptr);
    vis.setRangeBufferPointer(range_visualizeptr);
    // this isn't used in what appears to be thier most recent test
    // vis.setAngleMapPointer(angleMap_ptr);

    // FRAME POINTER INITIATION
    auto frame_daq = daq.getFramePointer();
    rdm.setFramePointer(frame_daq);
    auto frame_rdm = rdm.getFramePointer();
    daq.setFramePointer(frame_rdm);
    // OTHER PARAMS
    if (argc > 1){
        if(argc != 3){
            std::cout << "Incorrect number of arguments, format should be : \n    --> ./test max_SNR_THRESHOLD min_SNR_THRESHOLD \n OR --> ./test" << std::endl;
            return 1;
        }
        float max = std::stof(argv[1]);
        float min = std::stof(argv[2]);
        rdm.setSNR(max,min);
    }
    vis.setWaitTime(1);   

    rdm.process();
    
    int i = 1;
    while(true){
        daq.process();
        rdm.process();
        vis.process();
	i = i + 1;
    }

    return 0;
}
