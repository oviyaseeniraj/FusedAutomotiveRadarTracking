# Run Sync Program

## SSH into Jetsens

```bash
# From your laptop - SSH into Master
# Password: "fusionsense"
ssh fusionsense@169.231.215.235

# From your laptop - SSH into Slave (different terminal)
# Password: "password"
ssh fusionsense@169.231.22.160
```

## Copy Scripts to Jetsens

```bash
# From your laptop - navigate to project directory
cd /Users/oseeniraj/Chirp/Time-Synchronization

# Copy NTP files to Master
scp NTP/CHRONY_SETUP.sh fusionsense@169.231.215.235:~/

# Copy NTP files to Slave
scp NTP/CHRONY_SETUP.sh NTP/collect_offsets.py NTP/analyze_offsets.py NTP/requirements.txt fusionsense@169.231.22.160:~/

```

## Chrony Setup

On Master Jetson (169.231.215.235):
```bash
# SSH in
ssh fusionsense@169.231.215.235

# Install chrony
sudo apt-get update
sudo apt-get install -y chrony

# Configure as master
sudo bash -c 'cat > /etc/chrony/chrony.conf << EOF
local stratum 8
allow 169.231.0.0/16
logdir /var/log/chrony
rtcsync
makestep 1.0 3
EOF'

# Start chrony
sudo systemctl restart chrony
sudo systemctl enable chrony

# Verify
chronyc tracking
```
On Slave Jetson (169.231.22.160):
```bash
# SSH in
ssh fusionsense@169.231.22.160

# Install chrony
sudo apt-get update
sudo apt-get install -y chrony

# Configure as slave
sudo bash -c 'cat > /etc/chrony/chrony.conf << EOF
server 169.231.215.235 iburst prefer
pool time.google.com iburst
logdir /var/log/chrony
rtcsync
makestep 1.0 3
EOF'

# Start chrony
sudo systemctl restart chrony
sudo systemctl enable chrony

# Wait 30 seconds, then verify
sleep 30
chronyc sources -v
chronyc tracking
```

## Run Data Collection Scripts
On Slave Jetson (169.231.22.160):
```bash
# Install Python dependencies via apt (RECOMMENDED for Jetson)
sudo apt-get update
sudo apt-get install -y python3-numpy python3-scipy python3-matplotlib

# Verify installation
python3 -c "import numpy, scipy, matplotlib; print('OK')"

# Alternative: If pip3 is available
# pip3 install numpy scipy matplotlib
# Or: pip3 install -r requirements.txt

# Make scripts executable
chmod +x collect_offsets.py analyze_offsets.py

# Collect 100 samples (takes ~2 minutes)
python3 collect_offsets.py 100 1.0

# Note the output filename, e.g., offset_data_20251106_194523.json

# Analyze the data
python3 analyze_offsets.py offset_data_20251106_194523.json

# Or with plots
python3 analyze_offsets.py offset_data_20251106_194523.json --plot
```

Copy results back to laptop:
```bash
# From your laptop
scp fusionsense@169.231.22.160:~/offset_data_*.json .
scp fusionsense@169.231.22.160:~/offset_data_*_summary.json .
scp fusionsense@169.231.22.160:~/offset_data_*_plot.png .

# Then analyze locally if needed
python3 analyze_offsets.py offset_data_20251106_194523.json --plot
```

---

## Quick Test Commands

Monitor sync status continuously:
```bash
# On slave
watch -n 1 'chronyc tracking'
```
Check if master is reachable:
```bash
# On slave
chronyc sources -v
```
Restart if needed:
```bash
sudo systemctl restart chrony
```
