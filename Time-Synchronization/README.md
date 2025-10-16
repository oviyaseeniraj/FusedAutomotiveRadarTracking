# Time Synchronization for Wireless Radar Nodes

NTP with Kalman filtering for time synchronization between radar nodes over wireless/cellular networks.

**Goal**: Synchronize 2 devices to < 10ms  
**Hardware**: Jetson Nano 2023 with wireless/cellular connection

---

## How to Test 2 Devices

### Setup Device 1 (Time Server)

**Terminal 1 - Start time server (keep running):**
```bash
cd Time-Synchronization/NTP

# Find your IP address first
ifconfig | grep "inet "    # Mac/Linux
ipconfig                   # Windows

# Start time server
python3 simple_time_server.py
```

**Terminal 2 - Test from Device 1:**
```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server localhost --samples 30 --device1 "Device-1"
```

### Test from Device 2

```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server <DEVICE_1_IP> --samples 30 --device1 "Device-2"
```
*Replace `<DEVICE_1_IP>` with Device 1's actual IP*

### Calculate Sync Error

```
Sync Error = |Device1_Mean_Offset - Device2_Mean_Offset|

Example:
  Device 1 Mean Offset: 45.234 ms
  Device 1 Mean Delay:  89.123 ms
  
  Device 2 Mean Offset: 46.891 ms
  Device 2 Mean Delay:  91.456 ms
  
  Sync Error = |45.234 - 46.891| = 1.657 ms ✓
```

---

## Key Features

### Kalman Filtering (NEW)
- Adaptive filtering for variable network delays
- Better performance on wireless/cellular connections
- Automatically reduces trust in high-delay measurements
- Helps filter out network jitter

### Output Shows
- **Mean Offset**: Average time difference from reference
- **Mean Delay**: Average network round-trip delay
- **Std Dev**: Variability in measurements
- Both are critical for wireless networks

---

## Expected Performance

| Connection | Mean Delay | Sync Accuracy |
|------------|------------|---------------|
| Wired LAN | 0.5-2ms | < 2ms |
| WiFi (local) | 2-10ms | 2-10ms |
| Cellular | 50-200ms | 5-50ms |

**Note**: Kalman filtering helps achieve better accuracy on cellular (typically 5-20ms vs 50-100ms raw)

---

## Troubleshooting

**High sync error (> 50ms)?**
- Increase samples: `--samples 50` or `--samples 100`
- Check Mean Delay - if > 200ms, network is unstable
- Run tests multiple times, network may be congested
- Consider using GPS sync if outdoor deployment

**Can't connect?**
- Check firewall (allow port 12300)
- Verify IP with `ping <ip>`
- Ensure both devices on same network

---

## Quick Commands

```bash
# Find IP
ifconfig | grep "inet "

# Device 1: Start server
python3 simple_time_server.py

# Device 1: Test
python3 test_sync_two_devices.py --server localhost --samples 30

# Device 2: Test
python3 test_sync_two_devices.py --server <DEVICE_1_IP> --samples 30
```

---

## For Better Accuracy (Future)

If < 10ms is not achievable on your cellular network:
1. **GPS/GNSS sync** - Sub-microsecond accuracy, independent of network
2. **Increase samples** - More samples = better filtering (try 50-100)
3. **Test at different times** - Network congestion varies
4. **Use wired connection** for initial testing/validation
