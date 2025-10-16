#!/usr/bin/env python3
"""
Simple NTP-like Time Server

This server responds to NTP requests and can be used for local testing
of time synchronization between devices on the same network.

Note: This is a simplified implementation for testing purposes.
For production use, consider using ntpd or chrony.
"""

import socket
import struct
import time
import threading
from datetime import datetime

# NTP epoch is 1900-01-01, Unix epoch is 1970-01-01
NTP_DELTA = 2208988800

def unix_to_ntp_time(unix_time):
    """Convert Unix timestamp to NTP timestamp format"""
    seconds = int(unix_time + NTP_DELTA)
    fraction = int((unix_time % 1.0) * 2**32)
    return seconds, fraction

class SimpleTimeServer:
    """Simple NTP-like time server for local testing"""
    
    def __init__(self, host='0.0.0.0', port=12300):
        """
        Initialize time server
        
        Args:
            host: Host address to bind to (0.0.0.0 for all interfaces)
            port: Port to listen on (use non-privileged port like 12300)
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.request_count = 0
        
    def handle_request(self, data, client_address):
        """Handle incoming NTP request"""
        
        if len(data) < 48:
            print(f"Invalid request from {client_address}: too short")
            return None
        
        # Record receive time
        receive_time = time.time()
        
        # Parse client transmit timestamp from request (bytes 40-47)
        unpacked = struct.unpack('!12I', data[0:48])
        
        # Prepare response
        # Copy request but modify certain fields
        response = bytearray(data)
        
        # Set LI=0, VN=4, Mode=4 (server)
        response[0] = 0x24
        
        # Set stratum to 2 (secondary reference)
        response[1] = 2
        
        # Get current time
        transmit_time = time.time()
        
        # Convert times to NTP format
        recv_sec, recv_frac = unix_to_ntp_time(receive_time)
        xmit_sec, xmit_frac = unix_to_ntp_time(transmit_time)
        
        # Set receive timestamp (bytes 32-39)
        struct.pack_into('!II', response, 32, recv_sec, recv_frac)
        
        # Set transmit timestamp (bytes 40-47)
        struct.pack_into('!II', response, 40, xmit_sec, xmit_frac)
        
        self.request_count += 1
        
        return bytes(response)
    
    def run(self):
        """Run the time server"""
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.running = True
            
            print("="*60)
            print("Simple Time Server Started")
            print("="*60)
            print(f"Listening on {self.host}:{self.port}")
            print(f"Time: {datetime.now().isoformat()}")
            print()
            print("Waiting for requests... (Press Ctrl+C to stop)")
            print()
            
            while self.running:
                try:
                    # Receive request with timeout to allow checking running flag
                    self.socket.settimeout(1.0)
                    data, client_address = self.socket.recvfrom(1024)
                    
                    print(f"[{self.request_count+1}] Request from {client_address[0]}:{client_address[1]} "
                          f"at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
                    
                    # Handle request and send response
                    response = self.handle_request(data, client_address)
                    
                    if response:
                        self.socket.sendto(response, client_address)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error handling request: {e}")
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup server resources"""
        self.running = False
        if self.socket:
            self.socket.close()
        
        print()
        print("="*60)
        print("Server Stopped")
        print(f"Total requests handled: {self.request_count}")
        print("="*60)
    
    def stop(self):
        """Stop the server"""
        self.running = False

def main():
    """Main function to run the time server"""
    import sys
    
    port = 12300
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    server = SimpleTimeServer(port=port)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()

if __name__ == "__main__":
    main()

