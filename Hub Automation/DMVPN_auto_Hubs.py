from sys import argv
import csv
import getpass
import netmiko
from netmiko import ConnectHandler

# Creditials
username = input('Username: ')
password = getpass.getpass('Password: ')
ikepsk = input ('IKE Pre-shared-key: ')

# Define Nodes
script, csv_file = argv
reader = csv.DictReader(open(csv_file, 'rt'))

# Define all Hubs
all_hubs = []
for line in reader:
    all_hubs.append(line)
 
#Configure IKEv1 Crypto
for devices in all_hubs:
    devices['username'] = username
    devices['password'] = password
    net_connect = ConnectHandler(**devices)
    config_commands = ['crypto keyring DMVPN vrf WAN1',
    'pre-shared-key address 0.0.0.0 key %s' %ikepsk,
    'crypto isakmp policy 10',
    'authentication pre-share',
    'encryption aes 256',
    'hash sha256',
    'lifetime 28800',
    'crypto isakmp profile DMVPN_isakmp',
    'match identity address 0.0.0.0',
    'keyring DMVPN',
    'vrf WAN1',
    'crypto ipsec transform-set ESP-AES256-SHA2 esp-aes 256 esp-sha256-hmac',
    'crypto ipsec profile DMVPN_ipsec',
    'set transform-set ESP-AES256-SHA2',
    'set pfs group14']
    output = net_connect.send_config_set(config_commands)
    #print(output)

# Configure Loopbacks
c = 1
for devices in all_hubs:
    devices['username'] = username
    devices['password'] = password
    net_connect = ConnectHandler(**devices)
    config_commands = ['interface loopback0',
    'ip address 10.99.99.' + str(c)+ ' 255.255.255.255']
    output = net_connect.send_config_set(config_commands)
    #print(output)
    c = c + 1

# Configure Hub Tunnels - Hub1 .1 Hub2 .2
h = 1
for devices in all_hubs:
    devices['username'] = username
    devices['password'] = password
    net_connect = ConnectHandler(**devices)
    config_commands = ['interface tunnel100',
    'ip address 10.255.254.' + str(h) + ' 255.255.255.0',
    'tunnel source gig0/0',
    'tunnel mode gre multipoint',
    'ip nhrp map multicast dynamic',
    'ip nhrp network-id 47884',
    'tunnel vrf WAN1',
    'tunnel protection ipsec profile DMVPN_ipsec']
    output = net_connect.send_config_set(config_commands)
    #print(output)
    h = h + 1

# EIGRP Configurations
for devices in all_hubs:
    devices['username'] = username
    devices['password'] = password
    net_connect = ConnectHandler(**devices)
    config_commands = ['router eigrp DMVPN',
    'address-family ipv4 unicast autonomous-system 1000',
    'network 10.0.0.0',
    'af-interface Tunnel100',
    'no next-hop-self',
    'no split-horizon']
    output = net_connect.send_config_set(config_commands)
    #print(output)
print ('DMVPN Hubs configured')