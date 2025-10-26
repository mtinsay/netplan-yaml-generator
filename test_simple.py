#!/usr/bin/env python3
"""
Simple test of the netplan generator

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

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("Testing basic netplan generator functionality...\n")
    
    # Test DHCP ethernet
    print("=== DHCP Ethernet ===")
    generator = NetplanGenerator()
    generator.add_ethernet("eth0", dhcp4=True)
    print(generator.to_yaml())
    
    # Test static ethernet
    print("=== Static Ethernet ===")
    generator = NetplanGenerator()
    generator.add_ethernet(
        "eth0", 
        dhcp4=False, 
        addresses=["192.168.1.100/24"],
        gateway4="192.168.1.1",
        nameservers=["8.8.8.8", "8.8.4.4"]
    )
    print(generator.to_yaml())
    
    # Test bond
    print("=== Bond ===")
    generator = NetplanGenerator()
    generator.add_bond("bond0", ["eth0", "eth1"], mode="active-backup")
    print(generator.to_yaml())
    
    # Test bridge
    print("=== Bridge ===")
    generator = NetplanGenerator()
    generator.add_bridge("br0", ["eth0", "eth1"])
    print(generator.to_yaml())
    
    print("All tests completed successfully!")

if __name__ == "__main__":
    test_basic_functionality()