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

def test_bond_ethernet_declarations():
    """Test that bond interfaces automatically create ethernet declarations"""
    print("\n=== Testing Bond Ethernet Declarations ===")
    generator = NetplanGenerator()
    generator.add_bond("bond0", ["eth0", "eth1"], mode="active-backup")
    
    config = generator.config
    
    # Verify ethernet declarations exist
    assert "ethernets" in config["network"], "Ethernets section should exist"
    assert "eth0" in config["network"]["ethernets"], "eth0 should be declared"
    assert "eth1" in config["network"]["ethernets"], "eth1 should be declared"
    
    # Verify dhcp4 is false for bond interfaces
    assert config["network"]["ethernets"]["eth0"]["dhcp4"] is False, "eth0 should have dhcp4: false"
    assert config["network"]["ethernets"]["eth1"]["dhcp4"] is False, "eth1 should have dhcp4: false"
    
    print("✓ Bond ethernet declarations test passed")

def test_bridge_ethernet_declarations():
    """Test that bridge interfaces automatically create ethernet declarations"""
    print("=== Testing Bridge Ethernet Declarations ===")
    generator = NetplanGenerator()
    generator.add_bridge("br0", ["eth0", "eth1"])
    
    config = generator.config
    
    # Verify ethernet declarations exist
    assert "ethernets" in config["network"], "Ethernets section should exist"
    assert "eth0" in config["network"]["ethernets"], "eth0 should be declared"
    assert "eth1" in config["network"]["ethernets"], "eth1 should be declared"
    
    # Verify dhcp4 is false for bridge interfaces
    assert config["network"]["ethernets"]["eth0"]["dhcp4"] is False, "eth0 should have dhcp4: false"
    assert config["network"]["ethernets"]["eth1"]["dhcp4"] is False, "eth1 should have dhcp4: false"
    
    print("✓ Bridge ethernet declarations test passed")

def test_static_without_addresses():
    """Test that static configuration without addresses sets dhcp4: false"""
    print("\n=== Testing Static Without Addresses ===")
    
    # Test ethernet
    generator = NetplanGenerator()
    generator.add_ethernet("eth0", dhcp4=False)
    yaml_output = generator.to_yaml()
    assert "dhcp4: false" in yaml_output, "Ethernet should have dhcp4: false when static without addresses"
    print("✓ Ethernet static without addresses test passed")
    
    # Test bond
    generator = NetplanGenerator()
    generator.add_bond("bond0", ["eth0", "eth1"], dhcp4=False)
    yaml_output = generator.to_yaml()
    assert "dhcp4: false" in yaml_output, "Bond should have dhcp4: false when static without addresses"
    print("✓ Bond static without addresses test passed")
    
    # Test bridge
    generator = NetplanGenerator()
    generator.add_bridge("br0", ["eth0", "eth1"], dhcp4=False)
    yaml_output = generator.to_yaml()
    assert "dhcp4: false" in yaml_output, "Bridge should have dhcp4: false when static without addresses"
    print("✓ Bridge static without addresses test passed")

def test_networkmanager_config():
    """Test NetworkManager minimal configuration generation"""
    print("\n=== Testing NetworkManager Configuration ===")
    
    from netplan_generator import generate_networkmanager_config
    
    yaml_output = generate_networkmanager_config()
    
    # Verify basic structure
    assert "network:" in yaml_output, "Should contain network section"
    assert "version: 2" in yaml_output, "Should contain version 2"
    assert "renderer: NetworkManager" in yaml_output, "Should use NetworkManager renderer"
    
    # Verify comments are present
    assert "nmcli" in yaml_output, "Should contain nmcli information"
    assert "nm-connection-editor" in yaml_output, "Should contain GUI tool information"
    assert "NetworkManager command-line interface" in yaml_output, "Should contain CLI description"
    
    print("✓ NetworkManager configuration test passed")

if __name__ == "__main__":
    test_basic_functionality()
    test_bond_ethernet_declarations()
    test_bridge_ethernet_declarations()
    test_static_without_addresses()
    test_networkmanager_config()