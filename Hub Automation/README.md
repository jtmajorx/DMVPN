# dmvpn_hub_automation
Basic script for automating DMVPN spoke configurations
Requires netmiko (pip3 install netmiko) run script with CSV containing mgmt IP. This script also assumes you're using a front door VRF.

python3 DMVPN_HUB.py hubs.csv