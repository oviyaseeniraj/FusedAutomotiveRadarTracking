#!/bin/bash
# Chrony NTP Setup for Jetson Synchronization
# ============================================
# This is the RECOMMENDED approach for production use.

echo "================================"
echo "Chrony NTP Setup for Jetsons"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "[ERROR] Please run as root (sudo)"
    exit 1
fi

# Install Chrony
echo "[1/4] Installing Chrony..."
apt-get update
apt-get install -y chrony

echo ""
echo "[2/4] Which Jetson is this?"
echo "  1) Master/Server (169.231.16.241)"
echo "  2) Slave/Client (169.231.209.82)"
read -p "Enter choice [1-2]: " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "[3/4] Configuring as NTP Server..."
    
    cat > /etc/chrony/chrony.conf <<EOF
# Chrony NTP Server Configuration
# ================================

# Use system clock as reference (local mode)
local stratum 8
manual

# Allow clients on local network
allow 169.231.0.0/16

# Serve time even if not synchronized to external source
local stratum 8

# Log directory
logdir /var/log/chrony

# Enable kernel synchronization
rtcsync

# Increase polling interval for stability
maxpoll 6

# Smooth time adjustments
smoothtime 400 0.001

# Step threshold (step if offset > 1 second)
makestep 1.0 3
EOF

    echo "[4/4] Starting Chrony server..."
    systemctl restart chrony
    systemctl enable chrony
    
    echo ""
    echo "=========================================="
    echo "✓ Master configured successfully!"
    echo "=========================================="
    echo ""
    echo "Verify with:"
    echo "  sudo chronyc sources"
    echo "  sudo chronyc clients"
    echo ""
    
elif [ "$choice" = "2" ]; then
    read -p "[3/4] Enter Master IP [169.231.16.241]: " master_ip
    master_ip=${master_ip:-169.231.16.241}
    
    echo ""
    echo "[4/4] Configuring as NTP Client..."
    
    cat > /etc/chrony/chrony.conf <<EOF
# Chrony NTP Client Configuration
# ================================

# Use local master as time source
server $master_ip iburst minpoll 0 maxpoll 4

# Fallback to internet NTP if local master unavailable
pool time.google.com iburst

# Log directory
logdir /var/log/chrony

# Enable kernel synchronization
rtcsync

# Increase polling frequency for faster convergence
minpoll 0
maxpoll 4

# Allow larger adjustments
maxdistance 10.0
maxdelay 0.1

# Smooth time adjustments
smoothtime 400 0.001

# Step threshold (step if offset > 1 second)
makestep 1.0 3
EOF

    echo "[4/4] Starting Chrony client..."
    systemctl restart chrony
    systemctl enable chrony
    
    echo ""
    echo "=========================================="
    echo "✓ Client configured successfully!"
    echo "=========================================="
    echo ""
    echo "Verify with:"
    echo "  sudo chronyc sources -v"
    echo "  sudo chronyc tracking"
    echo ""
    echo "Wait ~30 seconds for initial sync, then check offset:"
    echo "  watch -n 1 'chronyc tracking'"
    echo ""
    
else
    echo "[ERROR] Invalid choice"
    exit 1
fi

echo "Monitoring commands:"
echo "  chronyc sources    - Show time sources"
echo "  chronyc tracking   - Show sync status and offset"
echo "  chronyc sourcestats - Show source statistics"

