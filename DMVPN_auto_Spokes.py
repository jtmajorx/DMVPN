from sys import argv
import csv
import getpass
import netmiko
from netmiko import ConnectHandler

# Creditials
username = input('Username: ')
password = getpass.getpass('Password: ')

# Define Nodes
script, csv_file = argv
reader = csv.DictReader(open(csv_file, 'rt'))

# Define all Spokes
all_spokes = []
for line in reader:
    all_spokes.append(line)

#Configure IKEv1 Crypto
for devices in all_spokes:
    devices['username'] = username
    devices['password'] = password
    net_connect = ConnectHandler(**devices)
    config_commands = ['crypto keyring DMVPN vrf WAN1',
    'pre-shared-key address 0.0.0.0 key cad2334edz1',
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
c = 101
for devices in all_spokes:
    devices['username'] = username
    devices['password'] = password
    net_connect = ConnectHandler(**devices)
    config_commands = ['interface loopback0',
    'ip address 10.99.99.' + str(c)+ ' 255.255.255.255']
    output = net_connect.send_config_set(config_commands)
    #print(output)
    c = c + 1

# Configure Spoke Tunnels - IP starting at 10 and incrementing by 1
a = 10
for devices in all_spokes:
    net_connect = ConnectHandler(**devices)
    config_commands = ['interface tunnel100',
    'ip address 10.255.254.' + str(a)+ ' 255.255.255.0',
    'tunnel source gig0/0',
    'tunnel mode gre multipoint',
    'ip nhrp map multicast 192.168.122.11',
    'ip nhrp map multicast 192.168.122.12',
    'ip nhrp map 10.255.254.1 192.168.122.11',
    'ip nhrp map 10.255.254.2 192.168.122.12',
    'ip nhrp nhs 10.255.254.1 priority 10',
    'ip nhrp nhs 10.255.254.2',
    'ip nhrp network-id 47884',
    'tunnel vrf WAN1',
    'tunnel protection ipsec profile DMVPN_ipsec']
    output = net_connect.send_config_set(config_commands)
    #print(output)
    a = a + 1

# EIGRP Configurations
for devices in all_spokes:
    devices['username'] = username
    devices['password'] = password
    net_connect = ConnectHandler(**devices)
    config_commands = ['router eigrp DMVPN',
    'address-family ipv4 unicast autonomous-system 1000',
    'network 10.0.0.0',
    'eigrp stub']
    output = net_connect.send_config_set(config_commands)
    #print(output)
print ('DMVPN Spokes Configured')