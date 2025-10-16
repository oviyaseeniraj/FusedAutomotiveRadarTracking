# Quick Start Guide: Testing Time Sync on 2 Devices

## Overview
This guide helps you quickly test NTP-based time synchronization between 2 devices to meet Milestone #1 requirements.

## What You Need
- 2 computers/laptops (Mac, Linux, or Windows with Python)
- Network connection between them (Ethernet cable or WiFi)
- Python 3.7 or higher on both devices

## Option A: Local Time Server Test (Recommended - Most Accurate)

This method gives you the most accurate measurement because both devices sync to a local server with minimal network delay.

### Step 1: Setup Device 1 (Time Server)

1. Open terminal on Device 1
2. Navigate to the project:
   ```bash
   cd Time-Synchronization/NTP
   ```

3. Find your IP address:
   ```bash
   # On Mac/Linux:
   ifconfig | grep "inet "
   
   # On Windows:
   ipconfig
   ```
   
   Look for your local IP (e.g., `192.168.1.100`)

4. Start the time server:
   ```bash
   python3 simple_time_server.py
   ```
   
   Keep this running! You should see: "Listening on 0.0.0.0:12300"

### Step 2: Test from Device 1 (same machine as server)

1. Open a **NEW terminal** on Device 1
2. Navigate to testing folder:
   ```bash
   cd Time-Synchronization/Testing
   ```

3. Run the test pointing to localhost:
   ```bash
   python3 test_sync_two_devices.py --server localhost --samples 20 --device1 "Laptop-1"
   ```

4. **Save the results** - you'll see something like:
   ```
   ✓ Laptop-1 Results:
     Mean Offset:    2.345 ms
     Median Offset:  2.321 ms
   ```
   
   Write down the **Mean Offset** value!

### Step 3: Test from Device 2

1. On Device 2, navigate to the same folder:
   ```bash
   cd Time-Synchronization/Testing
   ```

2. Run the test pointing to Device 1's IP:
   ```bash
   python3 test_sync_two_devices.py --server 192.168.1.100 --samples 20 --device1 "Laptop-2"
   ```
   
   Replace `192.168.1.100` with Device 1's actual IP address.

3. **Save the results** - note the Mean Offset value!

### Step 4: Calculate Sync Accuracy

```
Sync Error = |Device1_Offset - Device2_Offset|

Example:
  Device 1 Mean Offset: 2.345 ms
  Device 2 Mean Offset: 3.123 ms
  
  Sync Error = |2.345 - 3.123| = 0.778 ms ✓
```

**Target: < 10 ms** (Milestone #2 goal)

---

## Option B: Public NTP Server Test (Simpler Setup)

This method is easier but less accurate due to internet delays.

### On BOTH Devices (run separately):

```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server pool.ntp.org --samples 20
```

**Compare the Mean Offset values** between both devices to calculate sync error.

---

## Option C: Continuous Monitoring (for deeper analysis)

Want to see how sync changes over time?

### Run on both devices:

```bash
cd Time-Synchronization/Testing
python3 continuous_sync_monitor.py --server pool.ntp.org --duration 60 --interval 1.0
```

This will:
- Measure sync every 1 second
- Run for 60 seconds
- Save results to CSV file
- Show statistics at the end

---

## Troubleshooting

### Can't connect to local server?

1. Check firewall - you may need to allow Python or port 12300
2. Verify both devices are on same network
3. Test with ping first:
   ```bash
   ping 192.168.1.100
   ```

### Results seem inconsistent?

- Use more samples: `--samples 50`
- Use wired Ethernet instead of WiFi
- Close bandwidth-heavy apps (streaming, downloads)
- Run test multiple times and average

### Need to test with 4 devices?

Just repeat the process on 4 machines:
1. Run time server on Device 1
2. Run test on all 4 devices
3. Compare all pairs of offsets


## Quick Reference: All Commands

```bash
# Find IP address
ifconfig | grep "inet "

# Start time server
python3 simple_time_server.py

# Test with local server
python3 test_sync_two_devices.py --server 192.168.1.100 --samples 20

# Test with public NTP
python3 test_sync_two_devices.py --server pool.ntp.org --samples 20

# Continuous monitoring
python3 continuous_sync_monitor.py --server pool.ntp.org --duration 60
```

