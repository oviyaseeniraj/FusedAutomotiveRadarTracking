# Minimal C++ to Python Calibration Integration

Ultra-simple integration: C++ collects data → Python calibrates → Done.

## Complete Setup Guide for Jetson

### Step 1: Copy Files to Jetson

From your **Mac Terminal**:

```bash
# Copy calibration script
scp /Users/oseeniraj/Chirp/Self-Calibration/Simulation/Single-Target/calibrate.py \
    fusionsense@169.231.215.235:/home/fusionsense/calibrate.py

# Copy entire Node directory (if not already on Jetson)
scp -r /Users/oseeniraj/Chirp/Node \
    fusionsense@169.231.215.235:/home/fusionsense/repos/AVR/RadarPipeline/
```

### Step 2: Copy Updated Files to Jetson

From your **Mac Terminal**, copy the modified files:

```bash
# Copy updated implementation.cpp
scp /Users/oseeniraj/Chirp/Node/src/rpl/implementation.cpp \
    fusionsense@169.231.215.235:/home/fusionsense/repos/AVR/RadarPipeline/src/rpl/implementation.cpp

# Copy updated test.cpp
scp /Users/oseeniraj/Chirp/Node/test/non_thread/test.cpp \
    fusionsense@169.231.215.235:/home/fusionsense/repos/AVR/RadarPipeline/test/non_thread/test.cpp

# Copy calibrate.py
scp /Users/oseeniraj/Chirp/Self-Calibration/Simulation/Single-Target/calibrate.py \
    fusionsense@169.231.215.235:/home/fusionsense/calibrate.py
```

### Step 3: Install Dependencies on Jetson (If Needed)

SSH to Jetson and install required libraries:

```bash
ssh fusionsense@169.231.215.235

# Install Python dependencies (use apt-get, not pip3)
sudo apt-get update
sudo apt-get install python3-numpy python3-matplotlib -y

# Install C++ dependencies
sudo apt-get install libeigen3-dev rapidjson-dev -y

# Create Eigen symlink (required for compilation)
sudo ln -s /usr/include/eigen3/Eigen /usr/include/Eigen

# Verify Python dependencies
python3 -c 'import numpy; import matplotlib; print("Dependencies OK")'
```

### Step 4: Compile on Jetson

```bash
# Navigate to test directory
cd ~/repos/AVR/RadarPipeline/test/non_thread

# Compile test.cpp with calibration support
g++ -std=c++14 -Wall -Wextra -pedantic -I../../src/ -o test test.cpp \
    -lfftw3f -pthread -lm `pkg-config --cflags --libs opencv4`
```

### Step 5: Run Data Collection & Calibration

```bash
# Run the program (collects 100 frames, then auto-calibrates)
./test

# Or specify number of frames:
./test 200
```

The program will:
1. Collect radar data (angle/range per frame)
2. Save JSON files to `frame_data/`
3. Automatically run Python calibration
4. Save results to `frame_data/calibration_output/`

### Step 6: View Results on Jetson

```bash
# View calibration results
cat frame_data/calibration_output/calibration_results.txt

# List all output files
ls -la frame_data/calibration_output/
```

### Step 7: Copy Results to Your Mac

From your **Mac Terminal**:

```bash
# Copy results to your Desktop
scp -r fusionsense@169.231.215.235:~/repos/AVR/RadarPipeline/test/non_thread/frame_data/calibration_output \
    ~/Desktop/radar_results

# Open the folder to view plots
open ~/Desktop/radar_results
```

## What the Code Does

**Input**: JSON files with `Angle` and `Range` from each radar node  
**Process**: Converts polar→Cartesian, runs closed-form calibration algorithm  
**Output**: `frame_data/calibration_output/`
- `calibration_results.txt` - relative positions & orientations
- `calibration_{NodeName}.png` - visualization plots for each radar

## Example Output

```
RADAR CALIBRATION RESULTS
============================================================

Patrick as Reference:
--------------------------------------------------
  Mike: Position=(40.00, 0.00)m, Orientation=90.0°
  John: Position=(40.00, 40.00)m, Orientation=180.0°
  Sarah: Position=(0.00, 40.00)m, Orientation=270.0°
```

## Files Modified

- **calibrate.py** - Standalone Python script (reads C++ data, runs calibration)
- **test.cpp** - Modified to collect fixed frames + call calibration
- **implementation.cpp** - Added `run_calibration()` function (line ~155)

## Troubleshooting

**Compilation fails with "Eigen/Dense not found"**
```bash
sudo ln -s /usr/include/eigen3/Eigen /usr/include/Eigen
```

**Compilation fails with "rapidjson/document.h not found"**
```bash
sudo apt-get install rapidjson-dev -y
```

**Python script fails with "No module named numpy"**
```bash
sudo apt-get install python3-numpy python3-matplotlib -y
```

**No JSON files found**
```bash
# Make sure frame_data directory exists
mkdir -p /home/fusionsense/repos/AVR/RadarPipeline/test/non_thread/frame_data
```

## Manual Testing

Test calibration on existing data without running radar:

```bash
python3 /home/fusionsense/calibrate.py /path/to/data_directory
```

## Network Info

- **Jetson IP**: `169.231.215.235`
- **Username**: `fusionsense`
- **Data Path**: `~/repos/AVR/RadarPipeline/test/non_thread/frame_data`
- **Calibration Script**: `/home/fusionsense/calibrate.py`

## Quick Reference - All Commands

```bash
# 1. Copy files from Mac
scp /Users/oseeniraj/Chirp/Node/src/rpl/implementation.cpp fusionsense@169.231.215.235:/home/fusionsense/repos/AVR/RadarPipeline/src/rpl/implementation.cpp
scp /Users/oseeniraj/Chirp/Node/test/non_thread/test.cpp fusionsense@169.231.215.235:/home/fusionsense/repos/AVR/RadarPipeline/test/non_thread/test.cpp
scp /Users/oseeniraj/Chirp/Self-Calibration/Simulation/Single-Target/calibrate.py fusionsense@169.231.215.235:/home/fusionsense/calibrate.py

# 2. SSH and compile on Jetson
ssh fusionsense@169.231.215.235
cd ~/repos/AVR/RadarPipeline/test/non_thread
g++ -std=c++14 -Wall -Wextra -pedantic -I../../src/ -o test test.cpp -lfftw3f -pthread -lm `pkg-config --cflags --libs opencv4`
./test

# 3. Copy results back to Mac
scp -r fusionsense@169.231.215.235:~/repos/AVR/RadarPipeline/test/non_thread/frame_data/calibration_output ~/Desktop/radar_results
open ~/Desktop/radar_results
```

