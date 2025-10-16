# Time Synchronization for Multi-Radar Fusion

NTP-based time synchronization for testing 2 radar nodes.

**Goal**: Synchronize 2 devices to < 10ms

## Requirements
- 2 computers with Python 3.7+
- Network connection (Ethernet or WiFi)

---

## How to Test 2 Devices

### Option 1: Local Time Server (Recommended)

**On Device 1:**
```bash
cd Time-Synchronization/NTP

# Find your IP address
ifconfig | grep "inet "    # Mac/Linux
ipconfig                   # Windows

# Start time server
python3 simple_time_server.py
```

**On Device 1 (new terminal):**
```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server localhost --samples 20 --device1 "Device-1"
```

**On Device 2:**
```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server <DEVICE_1_IP> --samples 20 --device1 "Device-2"
```
*Replace `<DEVICE_1_IP>` with Device 1's actual IP address*

**Calculate Result:**
```
Sync Error = |Device1_Offset - Device2_Offset|

Example:
  Device 1 Mean Offset: 2.345 ms
  Device 2 Mean Offset: 3.123 ms
  Sync Error = 0.778 ms ✓ (within 10ms target)
```

---

### Option 2: Public NTP Server

**On both devices:**
```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server pool.ntp.org --samples 20
```

Compare the mean offsets to calculate sync error.

---

## Key Metrics

- **Sync Error**: The difference between Device 1 and Device 2 offsets
  - **Target: < 10ms**
- **RTT**: Round-trip time (lower is better)
  - Wired: 0.1-2ms (local) or 10-50ms (internet)
  - WiFi: 2-10ms (local) or 20-100ms (internet)

---

## Troubleshooting

**Can't connect?**
- Check firewall (allow port 12300)
- Verify IP address with `ping <ip>`
- Ensure both devices on same network

**High sync error?**
- Use wired Ethernet instead of WiFi
- Use more samples: `--samples 50`
- Close bandwidth-heavy applications
- Try local server instead of public NTP

**Python not found?**
- Try `python` instead of `python3`
- Verify Python 3.7+ with `python --version`

---

## Quick Commands

```bash
# Find IP
ifconfig | grep "inet "

# Start server (Device 1)
python3 simple_time_server.py

# Test from Device 1
python3 test_sync_two_devices.py --server localhost --samples 20

# Test from Device 2
python3 test_sync_two_devices.py --server <DEVICE_1_IP> --samples 20
```
