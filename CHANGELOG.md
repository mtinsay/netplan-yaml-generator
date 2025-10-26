# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-26

### Added
- Initial release of Netplan YAML Configuration Generator
- Command-line interface for generating netplan configurations
- Support for ethernet interfaces (DHCP and static IP)
- Support for bond interfaces with multiple bonding modes
- Support for bridge interfaces
- DHCP override configuration options
- Built-in YAML generator (no external dependencies)
- Comprehensive test suite
- Example usage scripts
- GPLv3 license
- Complete documentation and README

### Features
- **Ethernet interfaces**: DHCP or static IP configuration
- **Bond interfaces**: Multiple bonding modes (active-backup, 802.3ad, etc.)
- **Bridge interfaces**: For virtualization and container networking
- **DHCP overrides**: Custom DHCP client behavior
- **Flexible output**: stdout or file output
- **No dependencies**: Uses only built-in Python libraries
- **Networkd renderer**: Uses systemd-networkd as default renderer

### Supported Bond Modes
- balance-rr (Round-robin load balancing)
- active-backup (Active-backup failover - default)
- balance-xor (XOR hash load balancing)
- broadcast (Broadcast on all interfaces)
- 802.3ad (IEEE 802.3ad dynamic link aggregation)
- balance-tlb (Adaptive transmit load balancing)
- balance-alb (Adaptive load balancing)

### Documentation
- Complete README with usage examples
- Command-line help and examples
- Example scripts demonstrating various configurations
- Test suite for validation