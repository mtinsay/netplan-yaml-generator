#!/usr/bin/env python3
"""
Test script to verify ethernet declarations are automatically added for bonds and bridges

Copyright (C) 2025 Michael Tinsay

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from netplan_generator import NetplanGenerator

def test_bond_ethernet_declarations():
    """Test that bond creates ethernet declarations"""
    print("Testing bond ethernet declarations...")
    
    generator = NetplanGenerator()
    generator.add_bond("bond0", ["eth0", "eth1"], mode="active-backup")
    
    yaml_output = generator.to_yaml()
    print("Generated YAML:")
    print(yaml_output)
    
    # Verify the output contains ethernet declarations
    assert "ethernets:" in yaml_output
    assert "eth0:" in yaml_output
    assert "eth1:" in yaml_output
    assert "dhcp4: false" in yaml_output
    assert "bonds:" in yaml_output
    assert "bond0:" in yaml_output
    
    print("✓ Bond ethernet declarations test passed\n")

def test_bridge_ethernet_declarations():
    """Test that bridge creates ethernet declarations"""
    print("Testing bridge ethernet declarations...")
    
    generator = NetplanGenerator()
    generator.add_bridge("br0", ["eth0", "eth1"])
    
    yaml_output = generator.to_yaml()
    print("Generated YAML:")
    print(yaml_output)
    
    # Verify the output contains ethernet declarations
    assert "ethernets:" in yaml_output
    assert "eth0:" in yaml_output
    assert "eth1:" in yaml_output
    assert "dhcp4: false" in yaml_output
    assert "bridges:" in yaml_output
    assert "br0:" in yaml_output
    
    print("✓ Bridge ethernet declarations test passed\n")

def test_mixed_configuration():
    """Test mixed configuration with ethernet, bond, and bridge"""
    print("Testing mixed configuration...")
    
    generator = NetplanGenerator()
    
    # Add a regular ethernet interface
    generator.add_ethernet("eth0", dhcp4=True)
    
    # Add a bond (should create ethernet declarations for eth1, eth2)
    generator.add_bond("bond0", ["eth1", "eth2"], mode="active-backup", dhcp4=False, addresses=["10.0.1.100/24"])
    
    # Add a bridge (should create ethernet declaration for eth3)
    generator.add_bridge("br0", ["eth3"], dhcp4=True)
    
    yaml_output = generator.to_yaml()
    print("Generated YAML:")
    print(yaml_output)
    
    # Verify all sections exist
    assert "ethernets:" in yaml_output
    assert "bonds:" in yaml_output
    assert "bridges:" in yaml_output
    
    # Verify ethernet interfaces
    assert "eth0:" in yaml_output  # Regular ethernet
    assert "eth1:" in yaml_output  # Bond interface
    assert "eth2:" in yaml_output  # Bond interface
    assert "eth3:" in yaml_output  # Bridge interface
    
    # Verify DHCP settings
    lines = yaml_output.split('\n')
    eth0_dhcp = False
    eth1_dhcp = False
    eth2_dhcp = False
    eth3_dhcp = False
    
    for i, line in enumerate(lines):
        if "eth0:" in line and i+1 < len(lines):
            if "dhcp4: true" in lines[i+1]:
                eth0_dhcp = True
        elif "eth1:" in line and i+1 < len(lines):
            if "dhcp4: false" in lines[i+1]:
                eth1_dhcp = True
        elif "eth2:" in line and i+1 < len(lines):
            if "dhcp4: false" in lines[i+1]:
                eth2_dhcp = True
        elif "eth3:" in line and i+1 < len(lines):
            if "dhcp4: false" in lines[i+1]:
                eth3_dhcp = True
    
    assert eth0_dhcp, "eth0 should have dhcp4: true"
    assert eth1_dhcp, "eth1 should have dhcp4: false"
    assert eth2_dhcp, "eth2 should have dhcp4: false"
    assert eth3_dhcp, "eth3 should have dhcp4: false"
    
    print("✓ Mixed configuration test passed\n")

def test_static_without_addresses():
    """Test that --static without --addresses creates dhcp4: false"""
    print("Testing static configuration without addresses...")
    
    # Test ethernet
    generator = NetplanGenerator()
    generator.add_ethernet("eth0", dhcp4=False)  # Simulates --static without --addresses
    
    yaml_output = generator.to_yaml()
    print("Ethernet static without addresses:")
    print(yaml_output)
    
    assert "dhcp4: false" in yaml_output or "dhcp4: no" in yaml_output
    print("✓ Ethernet static without addresses test passed\n")
    
    # Test bond
    generator = NetplanGenerator()
    generator.add_bond("bond0", ["eth0", "eth1"], dhcp4=False)  # Simulates --static without --addresses
    
    yaml_output = generator.to_yaml()
    print("Bond static without addresses:")
    print(yaml_output)
    
    assert "dhcp4: false" in yaml_output or "dhcp4: no" in yaml_output
    print("✓ Bond static without addresses test passed\n")
    
    # Test bridge
    generator = NetplanGenerator()
    generator.add_bridge("br0", ["eth0", "eth1"], dhcp4=False)  # Simulates --static without --addresses
    
    yaml_output = generator.to_yaml()
    print("Bridge static without addresses:")
    print(yaml_output)
    
    assert "dhcp4: false" in yaml_output or "dhcp4: no" in yaml_output
    print("✓ Bridge static without addresses test passed\n")

if __name__ == "__main__":
    print("Testing Python netplan generator ethernet declarations\n")
    test_bond_ethernet_declarations()
    test_bridge_ethernet_declarations()
    test_mixed_configuration()
    test_static_without_addresses()
    print("🎉 All tests passed! Python program correctly adds ethernet declarations.")