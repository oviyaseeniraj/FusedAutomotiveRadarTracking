#!/usr/bin/env python3
"""
NTP Client for Time Synchronization Testing

This script queries an NTP server and calculates the time offset and round-trip delay.
Can be used to test time synchronization between local devices.
"""

import socket
import struct
import time
import sys
from datetime import datetime, timezone

# NTP epoch is 1900-01-01, Unix epoch is 1970-01-01
# Difference in seconds
NTP_DELTA = 2208988800

def ntp_time_to_unix(ntp_time):
    """Convert NTP timestamp to Unix timestamp"""
    return ntp_time - NTP_DELTA

def unix_to_ntp_time(unix_time):
    """Convert Unix timestamp to NTP timestamp"""
    return unix_time + NTP_DELTA

def get_ntp_time(server='pool.ntp.org', port=123, timeout=5):
    """
    Query an NTP server and get time information
    
    Args:
        server: NTP server address (hostname or IP)
        port: NTP port (default 123)
        timeout: Socket timeout in seconds
        
    Returns:
        dict with keys: offset, delay, server_time, local_time, stratum
    """
    
    # NTP packet format (48 bytes)
    # First byte: LI (2 bits), VN (3 bits), Mode (3 bits)
    # LI = 0 (no warning), VN = 3 (NTPv3), Mode = 3 (client)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(timeout)
    
    # Construct NTP request packet
    # First byte: 0x1B = 00 011 011 (LI=0, VN=3, Mode=3)
    data = b'\x1b' + 47 * b'\0'
    
    try:
        # Record transmission time
        t1 = time.time()
        
        # Send request
        client.sendto(data, (server, port))
        
        # Receive response
        data, address = client.recvfrom(1024)
        
        # Record reception time
        t4 = time.time()
        
        if len(data) < 48:
            raise Exception("Invalid NTP response")
        
        # Unpack the response
        unpacked = struct.unpack('!12I', data[0:48])
        
        # Extract important fields
        # Stratum (8 bits) - indicates quality/distance from reference clock
        stratum = (unpacked[0] >> 16) & 0xFF
        
        # Server transmit timestamp (bytes 40-47)
        # NTP timestamp is 64 bits: 32 bits for seconds, 32 bits for fraction
        tx_timestamp_sec = unpacked[10]
        tx_timestamp_frac = unpacked[11]
        
        # Convert to float (seconds since NTP epoch)
        t3_ntp = tx_timestamp_sec + tx_timestamp_frac / 2**32
        t3 = ntp_time_to_unix(t3_ntp)
        
        # Server receive timestamp (bytes 32-39)
        rx_timestamp_sec = unpacked[8]
        rx_timestamp_frac = unpacked[9]
        t2_ntp = rx_timestamp_sec + rx_timestamp_frac / 2**32
        t2 = ntp_time_to_unix(t2_ntp)
        
        # Calculate offset and delay
        # Offset: ((t2 - t1) + (t3 - t4)) / 2
        # Delay: (t4 - t1) - (t3 - t2)
        offset = ((t2 - t1) + (t3 - t4)) / 2
        delay = (t4 - t1) - (t3 - t2)
        
        return {
            'server': server,
            'offset': offset,
            'delay': delay,
            'rtt': t4 - t1,
            'server_time': t3,
            'local_time': t4,
            'stratum': stratum,
            'synchronized_time': time.time() + offset
        }
        
    except socket.timeout:
        raise Exception(f"Timeout connecting to NTP server {server}")
    except Exception as e:
        raise Exception(f"Error querying NTP server: {e}")
    finally:
        client.close()

def sync_with_ntp(server='pool.ntp.org', samples=5):
    """
    Synchronize with NTP server using multiple samples
    
    Args:
        server: NTP server address
        samples: Number of samples to take (median is used)
        
    Returns:
        dict with sync information
    """
    results = []
    
    print(f"Querying NTP server {server} ({samples} samples)...")
    
    for i in range(samples):
        try:
            result = get_ntp_time(server)
            results.append(result)
            print(f"  Sample {i+1}/{samples}: offset={result['offset']*1000:.2f}ms, delay={result['delay']*1000:.2f}ms")
            time.sleep(0.2)  # Small delay between samples
        except Exception as e:
            print(f"  Sample {i+1}/{samples}: Failed - {e}")
    
    if not results:
        raise Exception("All NTP queries failed")
    
    # Sort by delay (prefer lower delay samples)
    results.sort(key=lambda x: x['delay'])
    
    # Use median of best half
    best_half = results[:max(1, len(results)//2)]
    avg_offset = sum(r['offset'] for r in best_half) / len(best_half)
    avg_delay = sum(r['delay'] for r in best_half) / len(best_half)
    
    return {
        'server': server,
        'offset': avg_offset,
        'delay': avg_delay,
        'samples': len(results),
        'stratum': results[0]['stratum']
    }

def main():
    """Main function for testing NTP client"""
    
    if len(sys.argv) > 1:
        server = sys.argv[1]
    else:
        server = 'pool.ntp.org'
    
    print("="*60)
    print("NTP Time Synchronization Client")
    print("="*60)
    print()
    
    try:
        result = sync_with_ntp(server)
        
        print()
        print("="*60)
        print("RESULTS:")
        print("="*60)
        print(f"Server:         {result['server']}")
        print(f"Stratum:        {result['stratum']}")
        print(f"Time Offset:    {result['offset']*1000:.3f} ms")
        print(f"Round-trip:     {result['delay']*1000:.3f} ms")
        print(f"Samples Used:   {result['samples']}")
        print()
        
        if abs(result['offset'] * 1000) < 10:
            print("✓ Time synchronized within 10ms target!")
        else:
            print("✗ Time offset exceeds 10ms target")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

