class RadarBlock {
    public:
        int inputsize;
        int outputsize;
        bool verbose;

        uint frame = 0;

        uint *inputframeptr;
        float *inputbufferptr;
        float *inputangbufferptr;
        float *inputrangebuffptr;
        int *inputangindexptr;

        uint lastframe;

        // constructor
        RadarBlock(int size_in, int size_out, bool v = false) : outputbuffer(new float[size_out]) {
            inputsize = size_in;
            outputsize = size_out;
            verbose = v;
            printf("New %s created.\n", typeid(*this).name());
        }

        // deconstructor
        ~RadarBlock() {
            delete[] outputbuffer;
            printf("%s destroyed.\n", typeid(*this).name());
        }

        // public functions
        void setBufferPointer(float *ptr) {
            inputbufferptr = ptr;
        }

        void setRangeBufferPointer(float *ptr) {
            inputrangebuffptr = ptr;
        }

        void setAngleBufferPointer(float *ptr) {
            inputangbufferptr = ptr;
        }

        void setAngleIndexPointer(int *ptr) {
            inputangindexptr = ptr;
        }

        // Sets the input frame pointer
        void setFramePointer(uint *ptr) {
            inputframeptr = ptr;
            lastframe = *ptr;
        }

        // Retrieve outputbuffer pointer
        float *getBufferPointer() {
            return outputbuffer;
        }

        // Retrieve frame pointer
        uint *getFramePointer() {
            return &frame;
        }

        // Complete desired calculations / data manipulation
        virtual void process() {
            printf("Process done!\n");
        }

        // Iterates
        void iteration() {
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

    private:
        float *outputbuffer;

        // private functions
        // Listens for previous block (overwritten in some cases)
        virtual void listen() {
            for (;;) {
                if (*inputframeptr != lastframe) {
                    lastframe = *inputframeptr;
                    break;
                }
            }
        }

        void increment_frame() {
            frame++;
        }
};