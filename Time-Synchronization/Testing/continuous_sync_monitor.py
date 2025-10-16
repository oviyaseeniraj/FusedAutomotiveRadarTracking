#!/usr/bin/env python3
"""
Continuous Time Synchronization Monitor

Continuously monitors time synchronization offset and logs statistics.
Useful for long-term testing and stability analysis.
"""

import sys
import time
import csv
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '..')

try:
    from NTP.ntp_client import get_ntp_time
except ImportError:
    from ntp_client import get_ntp_time

class SyncMonitor:
    """Continuous synchronization monitor"""
    
    def __init__(self, server, interval=1.0, log_file=None):
        """
        Initialize monitor
        
        Args:
            server: Time server address
            interval: Measurement interval in seconds
            log_file: Optional CSV file to log results
        """
        self.server = server
        self.interval = interval
        self.log_file = log_file
        self.measurements = []
        
    def run(self, duration=None, max_samples=None):
        """
        Run continuous monitoring
        
        Args:
            duration: Optional duration in seconds (None = infinite)
            max_samples: Optional max number of samples (None = infinite)
        """
        
        print("="*70)
        print("CONTINUOUS TIME SYNCHRONIZATION MONITOR")
        print("="*70)
        print(f"Server:   {self.server}")
        print(f"Interval: {self.interval}s")
        if duration:
            print(f"Duration: {duration}s")
        if max_samples:
            print(f"Max Samples: {max_samples}")
        print()
        print("Press Ctrl+C to stop")
        print("="*70)
        print()
        
        # Setup CSV logging
        csv_writer = None
        csv_file = None
        if self.log_file:
            csv_file = open(self.log_file, 'w', newline='')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Timestamp', 'Offset_ms', 'Delay_ms', 'RTT_ms'])
        
        start_time = time.time()
        sample_count = 0
        
        try:
            while True:
                try:
                    # Take measurement
                    result = get_ntp_time(self.server)
                    
                    offset_ms = result['offset'] * 1000
                    delay_ms = result['delay'] * 1000
                    rtt_ms = result['rtt'] * 1000
                    
                    timestamp = datetime.now()
                    
                    self.measurements.append({
                        'timestamp': timestamp,
                        'offset': offset_ms,
                        'delay': delay_ms,
                        'rtt': rtt_ms
                    })
                    
                    sample_count += 1
                    
                    # Display
                    status = "✓" if abs(offset_ms) < 10 else "✗"
                    print(f"[{sample_count:4d}] {timestamp.strftime('%H:%M:%S.%f')[:-3]} | "
                          f"Offset: {offset_ms:>7.2f}ms | "
                          f"Delay: {delay_ms:>6.2f}ms | "
                          f"RTT: {rtt_ms:>6.2f}ms {status}")
                    
                    # Log to CSV
                    if csv_writer:
                        csv_writer.writerow([
                            timestamp.isoformat(),
                            f"{offset_ms:.3f}",
                            f"{delay_ms:.3f}",
                            f"{rtt_ms:.3f}"
                        ])
                        csv_file.flush()
                    
                    # Check termination conditions
                    if max_samples and sample_count >= max_samples:
                        break
                    
                    if duration and (time.time() - start_time) >= duration:
                        break
                    
                    # Wait for next measurement
                    time.sleep(self.interval)
                    
                except Exception as e:
                    print(f"[{sample_count:4d}] Error: {e}")
                    time.sleep(self.interval)
                    
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
        finally:
            if csv_file:
                csv_file.close()
            
            self.print_statistics()
    
    def print_statistics(self):
        """Print summary statistics"""
        
        if not self.measurements:
            print("\nNo measurements recorded")
            return
        
        offsets = [m['offset'] for m in self.measurements]
        delays = [m['delay'] for m in self.measurements]
        rtts = [m['rtt'] for m in self.measurements]
        
        print()
        print("="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        print(f"Total Samples:    {len(self.measurements)}")
        print(f"Duration:         {(self.measurements[-1]['timestamp'] - self.measurements[0]['timestamp']).total_seconds():.1f}s")
        print()
        print("Time Offset (ms):")
        print(f"  Mean:           {sum(offsets)/len(offsets):>8.3f}")
        print(f"  Min:            {min(offsets):>8.3f}")
        print(f"  Max:            {max(offsets):>8.3f}")
        print(f"  Range:          {max(offsets)-min(offsets):>8.3f}")
        if len(offsets) > 1:
            import statistics
            print(f"  Std Dev:        {statistics.stdev(offsets):>8.3f}")
        print()
        print("Round-Trip Time (ms):")
        print(f"  Mean:           {sum(rtts)/len(rtts):>8.3f}")
        print(f"  Min:            {min(rtts):>8.3f}")
        print(f"  Max:            {max(rtts):>8.3f}")
        print()
        
        within_target = sum(1 for o in offsets if abs(o) < 10)
        within_7ms = sum(1 for o in offsets if abs(o) < 7)
        
        print(f"Samples within 10ms: {within_target}/{len(offsets)} ({100*within_target/len(offsets):.1f}%)")
        print(f"Samples within 7ms:  {within_7ms}/{len(offsets)} ({100*within_7ms/len(offsets):.1f}%)")
        print()
        
        if self.log_file:
            print(f"Results logged to: {self.log_file}")
        print("="*70)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Continuously monitor time synchronization'
    )
    
    parser.add_argument('--server', '-s', default='pool.ntp.org',
                       help='Time server address (default: pool.ntp.org)')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                       help='Measurement interval in seconds (default: 1.0)')
    parser.add_argument('--duration', '-d', type=float,
                       help='Duration in seconds (default: run until stopped)')
    parser.add_argument('--samples', '-n', type=int,
                       help='Max number of samples (default: unlimited)')
    parser.add_argument('--log', '-l',
                       help='CSV file to log results')
    
    args = parser.parse_args()
    
    # Auto-generate log filename if not provided
    if args.log is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.log = f"sync_log_{timestamp}.csv"
    
    monitor = SyncMonitor(args.server, args.interval, args.log)
    monitor.run(duration=args.duration, max_samples=args.samples)

if __name__ == "__main__":
    main()

