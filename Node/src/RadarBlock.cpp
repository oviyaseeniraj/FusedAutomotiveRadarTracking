#include "RadarBlock.h"

RadarBlock::RadarBlock(int size_in, int size_out, bool v = false) : outputbuffer(new float[size_out]) {
    inputsize = size_in;
    outputsize = size_out;
    verbose = v;
    printf("New %s created.\n", typeid(*this).name());
}

RadarBlock::~RadarBlock() {
    delete[] outputbuffer;
    printf("%s destroyed.\n", typeid(*this).name());
}

void RadarBlock::setBufferPointer(float *ptr) {
    inputbufferptr = ptr;
}

void RadarBlock::setRangeBufferPointer(float *ptr) {
    inputrangebuffptr = ptr;
}

void RadarBlock::setAngleBufferPointer(float *ptr) {
    inputangbufferptr = ptr;
}

void RadarBlock::setAngleIndexPointer(int *ptr) {
    inputangindexptr = ptr;
}

// Sets the input frame pointer
void RadarBlock::setFramePointer(uint *ptr) {
    inputframeptr = ptr;
    lastframe = *ptr;
}

// Retrieve outputbuffer pointer
float* RadarBlock::getBufferPointer() {
    return outputbuffer;
}

// Retrieve frame pointer
uint* RadarBlock::getFramePointer() {
    return &frame;
}

// Complete desired calculations / data manipulation
virtual void RadarBlock::process() {
    printf("Process done!\n");
}

// Iterates
void RadarBlock::iteration() {
    for (;;) {
        listen();
        // start timer
        auto start = chrono::high_resolution_clock::now();
        process();
        // stop timer
        auto stop = chrono::high_resolution_clock::now();
        if (verbose) {
            // calculate elapsed time in microseconds
            auto duration = chrono::duration_cast<chrono::microseconds>(stop - start);
            // print elapsed time
            cout << "Elapsed time: " << duration.count() << " microseconds" << endl;
        }
        increment_frame();
    }
}

virtual void RadarBlock::listen() {
    for (;;) {
        if (*inputframeptr != lastframe) {
            lastframe = *inputframeptr;
            break;
        }
    }
}

void RadarBlock::increment_frame() {
    frame++;
}