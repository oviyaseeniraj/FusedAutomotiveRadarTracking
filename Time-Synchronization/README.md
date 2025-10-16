# Time Synchronization for Multi-Radar Fusion

This directory contains implementations and testing tools for time synchronization between multiple radar nodes, as part of the FusionSense project.

## Overview

**Goal**: Synchronize multiple radar nodes to within 10ms (eventually < 7ms)

**Milestone 1**: Research and implement NTP-based synchronization for 2 local devices

## Directory Structure

```
Time-Synchronization/
├── NTP/
│   ├── ntp_client.py              # NTP client implementation
│   └── simple_time_server.py      # Local time server for testing
├── Testing/
│   ├── test_sync_two_devices.py   # Two-device sync testing
│   └── continuous_sync_monitor.py # Continuous monitoring tool
└── README.md                       # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# No external dependencies required - uses only Python standard library
python3 --version  # Ensure Python 3.7+
```

### 2. Test with Public NTP Server (Single Device)

```bash
cd Time-Synchronization/NTP
python3 ntp_client.py
```

This will query `pool.ntp.org` and show your device's time offset.

### 3. Test Two Devices with Local Time Server

This is the recommended approach for initial testing as it eliminates internet variability.

#### On Device 1 (Server):

```bash
cd Time-Synchronization/NTP
python3 simple_time_server.py
```

This starts a time server on port 12300. Note the IP address of Device 1.

#### On Device 2 (Client):

```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server <DEVICE_1_IP> --samples 20
```

Replace `<DEVICE_1_IP>` with Device 1's IP address (e.g., `192.168.1.100`).

#### On Device 1 (also as Client):

In another terminal:
```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server localhost --samples 20
```

### 4. Test Two Devices with Public NTP

#### On Both Devices:

```bash
cd Time-Synchronization/Testing
python3 test_sync_two_devices.py --server pool.ntp.org --samples 20
```

Compare the mean offsets from both devices to calculate synchronization accuracy.

## Testing Methodologies

### Method 1: Local Time Server (Recommended for Initial Testing)

**Advantages:**
- Eliminates internet latency variability
- Fixed, low RTT on wired connection
- Complete control over server
- Easy to debug

**Setup:**
1. Connect both devices to same network (preferably wired Ethernet)
2. Run `simple_time_server.py` on one device
3. Run tests from both devices against this server
4. Calculate sync error as: `|Device1_Offset - Device2_Offset|`

### Method 2: Public NTP Server

**Advantages:**
- Tests real-world scenario
- No setup required
- Tests internet-based synchronization

**Setup:**
1. Ensure both devices have internet access
2. Run tests on both devices against same NTP server
3. Compare offsets to determine sync accuracy

### Method 3: Continuous Monitoring

For long-term stability testing:

```bash
cd Time-Synchronization/Testing
python3 continuous_sync_monitor.py --server <SERVER> --interval 1.0 --duration 300
```

This monitors sync every 1 second for 5 minutes and generates statistics.

## Understanding the Results

### Key Metrics

- **Offset**: Time difference between your clock and reference clock
  - Target: < 10ms (Milestone #2)
  - Stretch goal: < 7ms (Milestone #4.1)
  
- **Delay/RTT**: Round-trip time to server
  - Lower is better
  - Wired Ethernet: typically 0.1-2ms (local), 10-50ms (internet)
  - WiFi: typically 2-10ms (local), 20-100ms (internet)

- **Sync Error** (between two devices): `|Device1_Offset - Device2_Offset|`
  - This is the actual synchronization accuracy between devices

### Example Output Interpretation

```
Device 1 Mean Offset: 2.345 ms
Device 2 Mean Offset: 3.123 ms

Sync Error = |2.345 - 3.123| = 0.778 ms ✓ (well within 10ms target)
```

## Testing Workflow for Two Devices

### Wired Ethernet Setup (Recommended First)

1. **Physical Setup**:
   - Connect both devices via Ethernet (direct or through switch)
   - Ensure devices can ping each other
   - Note IP addresses: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)

2. **Run Local Server Test**:
   ```bash
   # Device 1 (Server)
   python3 simple_time_server.py
   
   # Device 2 (Client) - in separate terminal
   python3 test_sync_two_devices.py --server <Device1_IP> --samples 30
   
   # Device 1 (also Client) - in separate terminal  
   python3 test_sync_two_devices.py --server localhost --samples 30
   ```

3. **Analyze Results**:
   - Record mean offsets from both devices
   - Calculate sync error
   - Check if RTT is stable (should be < 2ms on wired)

### Wireless Setup (After Wired Success)

Same procedure as wired, but:
- Expect higher RTT variability
- May need more samples for accurate average
- Test with both devices on 5GHz WiFi if possible

### Continuous Monitoring Test

```bash
# Run on both devices simultaneously
python3 continuous_sync_monitor.py --server pool.ntp.org --duration 300 --interval 1.0
```

Compare the statistics from both devices.

## Troubleshooting

### "Connection Refused" or "Timeout"

- Check firewall settings
- Verify IP address is correct
- Ensure time server is running (for local server)
- Try ping first: `ping <server_ip>`

### High RTT or Unstable Measurements

- Check network load (stop downloads/streaming)
- Use wired connection if possible
- Try different NTP server closer to your location:
  - `time.nist.gov` (US)
  - `time.google.com` (Global)
  - `time.cloudflare.com` (Global)

### Port 123 Permission Denied

- NTP uses privileged port 123
- Our local server uses port 12300 instead
- For real NTP client, may need sudo

### Inconsistent Results

- Take more samples (`--samples 50`)
- Increase monitoring duration
- Check for background processes affecting network
- Verify stable power/thermal conditions

## Next Steps (Future Milestones)

### Milestone #2: Optimize to < 10ms
- [ ] Implement averaging algorithms
- [ ] Add outlier detection
- [ ] Test with 4 devices
- [ ] Optimize measurement timing

### Milestone #3: Research Better Methods
- [ ] Implement PTP (Precision Time Protocol)
- [ ] Test MQTT-based synchronization
- [ ] Evaluate custom protocols
- [ ] Compare accuracy vs NTP

### Milestone #4: Integration
- [ ] Integrate with radar hardware
- [ ] Real-time synchronization during data collection
- [ ] Optimize to < 7ms
- [ ] Production deployment

## References

- [NTP Protocol Specification (RFC 5905)](https://tools.ietf.org/html/rfc5905)
- [PTP/IEEE 1588 Standard](https://standards.ieee.org/standard/1588-2019.html)
- [Network Time Synchronization Research Papers](https://scholar.google.com/scholar?q=network+time+synchronization)

## Notes

- Current implementation is educational/testing quality
- For production, consider: `ntpd`, `chrony`, or hardware PTP
- Measurement accuracy depends on network conditions
- Clock drift is not currently handled (system clock assumed stable)

