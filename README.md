# Netplan YAML Configuration Generator

A Python command-line tool that generates netplan YAML configurations for various network interface types including ethernet, bonds, and bridges.

## Features

- **Ethernet interfaces**: DHCP or static IP configuration
- **Bond interfaces**: Multiple bonding modes with failover support
- **Bridge interfaces**: For virtualization and container networking
- **DHCP overrides**: Custom DHCP client behavior
- **Flexible output**: stdout or file output
- **Networkd renderer**: Uses systemd-networkd as default renderer

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Examples

#### DHCP Ethernet Interface
```bash
python netplan_generator.py --ethernet eth0
```

#### Static Ethernet Interface
```bash
python netplan_generator.py --ethernet eth0 --static --addresses 192.168.1.100/24 --gateway4 192.168.1.1 --nameservers 8.8.8.8,8.8.4.4
```

#### Bond Interface
```bash
python netplan_generator.py --bond bond0 --bond-interfaces eth0,eth1 --bond-mode active-backup
```

#### Bridge Interface
```bash
python netplan_generator.py --bridge br0 --bridge-interfaces eth0,eth1
```

### Advanced Examples

#### DHCP Overrides
```bash
python netplan_generator.py --ethernet eth0 --dhcp4-overrides use-dns=false,use-ntp=false
```

#### Static Bond with 802.3ad
```bash
python netplan_generator.py --bond bond0 --bond-interfaces eth0,eth1 --bond-mode 802.3ad --static --addresses 10.0.1.100/24 --gateway4 10.0.1.1
```

#### NetworkManager Configuration
```bash
python netplan_generator.py --use-nm
```

#### Output to File
```bash
python netplan_generator.py --ethernet eth0 --output /etc/netplan/01-config.yaml
```

## Command Line Options

### General Options
- `--output, -o`: Output file path (default: stdout)
- `--renderer`: Network renderer (networkd or NetworkManager, default: networkd)
- `--use-nm`: Generate minimal NetworkManager configuration (ignores all other options)

### Interface Options
- `--ethernet`: Ethernet interface name
- `--bond`: Bond interface name  
- `--bridge`: Bridge interface name

### Configuration Options
- `--static`: Use static IP instead of DHCP
- `--addresses`: Comma-separated IP addresses with CIDR notation
- `--gateway4`: IPv4 gateway address
- `--gateway6`: IPv6 gateway address
- `--nameservers`: Comma-separated nameserver addresses
- `--dhcp4-overrides`: DHCP4 overrides (key=value,key=value)
- `--dhcp6-overrides`: DHCP6 overrides (key=value,key=value)

### Bond/Bridge Specific Options
- `--bond-interfaces`: Comma-separated interfaces for bond
- `--bond-mode`: Bond mode (default: active-backup)
- `--bridge-interfaces`: Comma-separated interfaces for bridge

## Supported Bond Modes

- `balance-rr`: Round-robin load balancing
- `active-backup`: Active-backup failover (default)
- `balance-xor`: XOR hash load balancing
- `broadcast`: Broadcast on all interfaces
- `802.3ad`: IEEE 802.3ad dynamic link aggregation
- `balance-tlb`: Adaptive transmit load balancing
- `balance-alb`: Adaptive load balancing

## Example Configurations

Run the examples script to see various configuration examples:

```bash
python examples.py
```

## Generated YAML Structure

The tool generates netplan-compliant YAML with the following structure:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
    eth1:
      dhcp4: false
    eth2:
      dhcp4: false
    eth3:
      dhcp4: false
  bonds:
    bond0:
      interfaces: [eth1, eth2]
      parameters:
        mode: active-backup
      dhcp4: true
  bridges:
    br0:
      interfaces: [eth3]
      dhcp4: true
```

## Testing

Run the simple test to verify functionality:

```bash
python test_simple.py
```

## Best Practices

1. **Test configurations**: Always test generated configurations in a safe environment
2. **Backup existing configs**: Keep backups of working netplan configurations
3. **Use descriptive names**: Choose meaningful interface names
4. **Validate YAML**: Ensure generated YAML is valid before applying
5. **Apply with netplan**: Use `netplan apply` to activate configurations

## Troubleshooting

- Ensure PyYAML is installed: `pip install PyYAML`
- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('config.yaml'))"`
- Test netplan config: `netplan try` (applies temporarily)
- Check netplan syntax: `netplan generate`