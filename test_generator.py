#!/usr/bin/env python3
"""
Simple tests for the netplan generator

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

import sys
import yaml
from netplan_generator import NetplanGenerator, EthernetConfig, BondConfig, BridgeConfig

def test_dhcp_ethernet():
    """Test DHCP ethernet configuration"""
    print("Testing DHCP ethernet...")
    generator = NetplanGenerator()
    
    eth_config = EthernetConfig(name="eth0", dhcp4=True)
    generator.add_ethernet(eth_config)
    
    config = generator.generate_config()
    
    # Validate structure
    assert config["network"]["version"] == 2
    assert config["network"]["renderer"] == "networkd"
    assert "ethernets" in config["network"]
    assert "eth0" in config["network"]["ethernets"]
    assert config["network"]["ethernets"]["eth0"]["dhcp4"] is True
    
    print("✓ DHCP ethernet test passed")

def test_static_ethernet():
    """Test static ethernet configuration"""
    print("Testing static ethernet...")
    generator = NetplanGenerator()
    
    eth_config = EthernetConfig(
        name="eth0",
        dhcp4=False,
        addresses=["192.168.1.100/24"],
        gateway4="192.168.1.1",
        nameservers={"addresses": ["8.8.8.8"]}
    )
    generator.add_ethernet(eth_config)
    
    config = generator.generate_config()
    eth_config_dict = config["network"]["ethernets"]["eth0"]
    
    assert "dhcp4" not in eth_config_dict or eth_config_dict["dhcp4"] is False
    assert eth_config_dict["addresses"] == ["192.168.1.100/24"]
    assert eth_config_dict["gateway4"] == "192.168.1.1"
    assert eth_config_dict["nameservers"]["addresses"] == ["8.8.8.8"]
    
    print("✓ Static ethernet test passed")

def test_bond():
    """Test bond configuration"""
    print("Testing bond...")
    generator = NetplanGenerator()
    
    bond_config = BondConfig(
        name="bond0",
        interfaces=["eth0", "eth1"],
        mode="active-backup",
        dhcp4=True
    )
    generator.add_bond(bond_config)
    
    config = generator.generate_config()
    bond_config_dict = config["network"]["bonds"]["bond0"]
    
    assert bond_config_dict["dhcp4"] is True
    assert bond_config_dict["interfaces"] == ["eth0", "eth1"]
    assert bond_config_dict["parameters"]["mode"] == "active-backup"
    
    print("✓ Bond test passed")

def test_bridge():
    """Test bridge configuration"""
    print("Testing bridge...")
    generator = NetplanGenerator()
    
    bridge_config = BridgeConfig(
        name="br0",
        interfaces=["eth0"],
        dhcp4=True
    )
    generator.add_bridge(bridge_config)
    
    config = generator.generate_config()
    bridge_config_dict = config["network"]["bridges"]["br0"]
    
    assert bridge_config_dict["dhcp4"] is True
    assert bridge_config_dict["interfaces"] == ["eth0"]
    
    print("✓ Bridge test passed")

def test_yaml_output():
    """Test YAML output generation"""
    print("Testing YAML output...")
    generator = NetplanGenerator()
    
    eth_config = EthernetConfig(name="eth0", dhcp4=True)
    generator.add_ethernet(eth_config)
    
    yaml_output = generator.to_yaml()
    
    # Validate that it's valid YAML
    try:
        parsed = yaml.safe_load(yaml_output)
        assert parsed["network"]["version"] == 2
        print("✓ YAML output test passed")
    except yaml.YAMLError as e:
        print(f"✗ YAML output test failed: {e}")
        sys.exit(1)

def test_complex_config():
    """Test complex configuration with multiple interface types"""
    print("Testing complex configuration...")
    generator = NetplanGenerator()
    
    # Add ethernet
    eth_config = EthernetConfig(name="eth0", dhcp4=True)
    generator.add_ethernet(eth_config)
    
    # Add bond
    bond_config = BondConfig(
        name="bond0",
        interfaces=["eth1", "eth2"],
        mode="active-backup",
        dhcp4=False,
        addresses=["10.0.1.100/24"]
    )
    generator.add_bond(bond_config)
    
    # Add bridge
    bridge_config = BridgeConfig(
        name="br0",
        interfaces=["eth3"],
        dhcp4=True
    )
    generator.add_bridge(bridge_config)
    
    config = generator.generate_config()
    
    # Validate all sections exist
    assert "ethernets" in config["network"]
    assert "bonds" in config["network"]
    assert "bridges" in config["network"]
    
    print("✓ Complex configuration test passed")

def main():
    """Run all tests"""
    print("Running netplan generator tests...\n")
    
    try:
        test_dhcp_ethernet()
        test_static_ethernet()
        test_bond()
        test_bridge()
        test_yaml_output()
        test_complex_config()
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()