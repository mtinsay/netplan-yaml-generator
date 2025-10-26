#!/usr/bin/env python3
"""
Example usage of the netplan generator

Copyright (C) 2025 Michael Tinsay

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from netplan_generator import NetplanGenerator

def example_dhcp_ethernet():
    """Example: Simple DHCP ethernet configuration"""
    print("=== DHCP Ethernet Example ===")
    generator = NetplanGenerator()
    generator.add_ethernet("eth0", dhcp4=True)
    print(generator.to_yaml())

def example_static_ethernet():
    """Example: Static ethernet configuration"""
    print("=== Static Ethernet Example ===")
    generator = NetplanGenerator()
    generator.add_ethernet(
        "eth0",
        dhcp4=False,
        addresses=["192.168.1.100/24"],
        gateway4="192.168.1.1",
        nameservers=["8.8.8.8", "8.8.4.4"]
    )
    print(generator.to_yaml())

def example_ethernet_with_overrides():
    """Example: Ethernet with DHCP overrides"""
    print("=== Ethernet with DHCP Overrides Example ===")
    generator = NetplanGenerator()
    generator.add_ethernet(
        "eth0",
        dhcp4=True,
        dhcp4_overrides={"use-dns": False, "use-ntp": False}
    )
    print(generator.to_yaml())

def example_bond():
    """Example: Bond configuration"""
    print("=== Bond Example ===")
    generator = NetplanGenerator()
    generator.add_bond(
        "bond0",
        interfaces=["eth0", "eth1"],
        mode="active-backup",
        dhcp4=True
    )
    print(generator.to_yaml())

def example_static_bond():
    """Example: Static bond configuration"""
    print("=== Static Bond Example ===")
    generator = NetplanGenerator()
    generator.add_bond(
        "bond0",
        interfaces=["eth0", "eth1"],
        mode="802.3ad",
        dhcp4=False,
        addresses=["10.0.1.100/24"],
        gateway4="10.0.1.1",
        nameservers=["1.1.1.1", "1.0.0.1"]
    )
    print(generator.to_yaml())

def example_bridge():
    """Example: Bridge configuration"""
    print("=== Bridge Example ===")
    generator = NetplanGenerator()
    generator.add_bridge(
        "br0",
        interfaces=["eth0", "eth1"],
        dhcp4=True
    )
    print(generator.to_yaml())

def example_static_bridge():
    """Example: Static bridge configuration"""
    print("=== Static Bridge Example ===")
    generator = NetplanGenerator()
    generator.add_bridge(
        "br0",
        interfaces=["eth0"],
        dhcp4=False,
        addresses=["192.168.100.1/24"]
    )
    print(generator.to_yaml())

def example_complex():
    """Example: Complex configuration with multiple interface types"""
    print("=== Complex Example ===")
    generator = NetplanGenerator()
    
    # Management interface with DHCP
    generator.add_ethernet("eth0", dhcp4=True)
    
    # Bond for high availability
    generator.add_bond(
        "bond0",
        interfaces=["eth1", "eth2"],
        mode="active-backup",
        dhcp4=False,
        addresses=["10.0.1.100/24"],
        gateway4="10.0.1.1"
    )
    
    # Bridge for VMs
    generator.add_bridge(
        "br0",
        interfaces=["eth3"],
        dhcp4=False,
        addresses=["192.168.100.1/24"]
    )
    
    print(generator.to_yaml())

if __name__ == "__main__":
    example_dhcp_ethernet()
    example_static_ethernet()
    example_ethernet_with_overrides()
    example_bond()
    example_static_bond()
    example_bridge()
    example_static_bridge()
    example_complex()