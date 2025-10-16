#!/usr/bin/env python3
"""
Time Synchronization Testing for Two Devices

This script measures the time synchronization accuracy between two devices
by querying a common time source (NTP server or local time server).
"""

import sys
import time
import socket
import struct
from datetime import datetime
import statistics

# Add parent directory to path for imports
sys.path.insert(0, '..')

try:
    from NTP.ntp_client import get_ntp_time, sync_with_ntp
except ImportError:
    # If running from different directory
    from ntp_client import get_ntp_time, sync_with_ntp

class TwoDeviceSync:
    """Test time synchronization between two devices"""
    
    def __init__(self, time_server, use_local_server=False):
        """
        Initialize sync tester
        
        Args:
            time_server: Address of time server (NTP or local)
            use_local_server: If True, use custom port 12300 for local server
        """
        self.time_server = time_server
        self.use_local_server = use_local_server
        self.port = 12300 if use_local_server else 123
        
    def measure_offset(self, num_samples=10):
        """
        Measure time offset from reference server
        
        Args:
            num_samples: Number of measurements to take
            
        Returns:
            dict with statistics
        """
        offsets = []
        delays = []
        rtts = []
        
        print(f"Measuring time offset ({num_samples} samples)...")
        
        for i in range(num_samples):
            try:
                if self.use_local_server:
                    # Query local time server
                    result = self._query_local_server()
                else:
                    # Query NTP server
                    result = get_ntp_time(self.time_server, self.port)
                
                offsets.append(result['offset'])
                delays.append(result['delay'])
                rtts.append(result['rtt'])
                
                print(f"  [{i+1}/{num_samples}] offset={result['offset']*1000:.3f}ms, "
                      f"delay={result['delay']*1000:.3f}ms")
                
                time.sleep(0.1)  # Small delay between samples
                
            except Exception as e:
                print(f"  [{i+1}/{num_samples}] Failed: {e}")
        
        if not offsets:
            raise Exception("All measurements failed")
        
        return {
            'mean_offset': statistics.mean(offsets),
            'median_offset': statistics.median(offsets),
            'stdev_offset': statistics.stdev(offsets) if len(offsets) > 1 else 0,
            'min_offset': min(offsets),
            'max_offset': max(offsets),
            'mean_delay': statistics.mean(delays),
            'mean_rtt': statistics.mean(rtts),
            'samples': len(offsets)
        }
    
    def _query_local_server(self):
        """Query local time server (simplified version)"""
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(5)
        
        # Construct NTP request
        data = b'\x1b' + 47 * b'\0'
        
        try:
            t1 = time.time()
            client.sendto(data, (self.time_server, self.port))
            data, address = client.recvfrom(1024)
            t4 = time.time()
            
            unpacked = struct.unpack('!12I', data[0:48])
            
            # Extract timestamps
            NTP_DELTA = 2208988800
            tx_timestamp = unpacked[10] + unpacked[11] / 2**32 - NTP_DELTA
            rx_timestamp = unpacked[8] + unpacked[9] / 2**32 - NTP_DELTA
            
            t2, t3 = rx_timestamp, tx_timestamp
            
            offset = ((t2 - t1) + (t3 - t4)) / 2
            delay = (t4 - t1) - (t3 - t2)
            
            return {
                'offset': offset,
                'delay': delay,
                'rtt': t4 - t1
            }
        finally:
            client.close()

def test_two_device_sync(device1_name, device2_name, time_server, samples=10):
    """
    Simulate/test synchronization between two devices
    
    Args:
        device1_name: Name of first device
        device2_name: Name of second device  
        time_server: Common time server address
        samples: Number of measurements per device
    """
    
    print("="*70)
    print("TWO DEVICE TIME SYNCHRONIZATION TEST")
    print("="*70)
    print(f"Device 1: {device1_name}")
    print(f"Device 2: {device2_name}")
    print(f"Time Server: {time_server}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    print()
    
    # Determine if using local server
    use_local = time_server not in ['pool.ntp.org', 'time.nist.gov', 
                                     'time.google.com', 'time.cloudflare.com']
    
    tester = TwoDeviceSync(time_server, use_local_server=use_local)
    
    # Measure Device 1 (this device)
    print(f"📱 {device1_name} - Measuring time offset from {time_server}")
    print("-"*70)
    try:
        device1_stats = tester.measure_offset(samples)
        print()
        print(f"✓ {device1_name} Results:")
        print(f"  Mean Offset:   {device1_stats['mean_offset']*1000:>8.3f} ms")
        print(f"  Mean Delay:    {device1_stats['mean_delay']*1000:>8.3f} ms")
        print(f"  Median Offset: {device1_stats['median_offset']*1000:>8.3f} ms")
        print(f"  Std Dev:       {device1_stats['stdev_offset']*1000:>8.3f} ms")
        print(f"  Range:         {device1_stats['min_offset']*1000:>8.3f} to {device1_stats['max_offset']*1000:.3f} ms")
    except Exception as e:
        print(f"✗ {device1_name} measurements failed: {e}")
        return
    
    print()
    print("="*70)
    print()
    
    # Instructions for Device 2
    print(f"📱 {device2_name} - INSTRUCTIONS")
    print("-"*70)
    print("Run this same script on the second device to get its measurements.")
    print()
    print("On Device 2, run:")
    if use_local:
        print(f"  python3 test_sync_two_devices.py {time_server} --samples {samples}")
    else:
        print(f"  python3 test_sync_two_devices.py --server {time_server} --samples {samples}")
    print()
    print("Then compare the mean offsets to determine relative sync accuracy.")
    print()
    
    # Estimate sync accuracy
    print("="*70)
    print("SYNCHRONIZATION ANALYSIS")
    print("="*70)
    print()
    print(f"Device 1 Mean Offset: {device1_stats['mean_offset']*1000:.3f} ms")
    print(f"Device 1 Mean Delay:  {device1_stats['mean_delay']*1000:.3f} ms")
    print()
    print("To calculate sync accuracy between devices:")
    print("  Sync Error = |Device1_Offset - Device2_Offset|")
    print()
    print(f"Target: < 10 ms")
    print(f"Status: {'✓ ON TRACK' if abs(device1_stats['mean_offset']*1000) < 10 else '⚠ NEEDS IMPROVEMENT'}")
    print()

def main():
    """Main testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test time synchronization between two devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with public NTP server
  python3 test_sync_two_devices.py --server pool.ntp.org
  
  # Test with local time server
  python3 test_sync_two_devices.py --server 192.168.1.100
  
  # More samples for better accuracy
  python3 test_sync_two_devices.py --server pool.ntp.org --samples 20
        """
    )
    
    parser.add_argument('--server', '-s', default='localhost',
                       help='Time server address (default: localhost)')
    parser.add_argument('--samples', '-n', type=int, default=10,
                       help='Number of measurements (default: 10)')
    parser.add_argument('--device1', default='Device-1',
                       help='Name of this device (default: Device-1)')
    parser.add_argument('--device2', default='Device-2',
                       help='Name of other device (default: Device-2)')
    
    args = parser.parse_args()
    
    try:
        test_two_device_sync(
            args.device1,
            args.device2,
            args.server,
            args.samples
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

