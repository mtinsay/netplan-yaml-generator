#!/usr/bin/env python3
"""
Netplan YAML Configuration Generator

A command-line tool to generate netplan YAML configurations for:
- Basic ethernet devices (DHCP or static)
- Bonds
- Bridges

Uses networkd as the default renderer and follows netplan documentation standards.

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

import argparse
import sys
import yaml
from typing import Dict, List, Optional, Any


class NetplanGenerator:
    """Main class for generating netplan configurations."""
    
    def __init__(self, renderer="networkd"):
        self.config = {
            "network": {
                "version": 2,
                "renderer": renderer
            }
        }
    
    def add_ethernet(self, name: str, dhcp4: bool = True, dhcp6: bool = False, 
                    addresses: List[str] = None, gateway4: str = None, 
                    gateway6: str = None, nameservers: List[str] = None,
                    dhcp4_overrides: Dict[str, Any] = None,
                    dhcp6_overrides: Dict[str, Any] = None) -> None:
        """Add ethernet interface configuration."""
        if "ethernets" not in self.config["network"]:
            self.config["network"]["ethernets"] = {}
        
        interface_config = {}
        
        if dhcp4:
            interface_config["dhcp4"] = True
        if dhcp6:
            interface_config["dhcp6"] = True
            
        if addresses:
            interface_config["addresses"] = addresses
            
        if gateway4:
            interface_config["gateway4"] = gateway4
        if gateway6:
            interface_config["gateway6"] = gateway6
            
        if nameservers:
            interface_config["nameservers"] = {"addresses": nameservers}
            
        if dhcp4_overrides:
            interface_config["dhcp4-overrides"] = dhcp4_overrides
        if dhcp6_overrides:
            interface_config["dhcp6-overrides"] = dhcp6_overrides
            
        self.config["network"]["ethernets"][name] = interface_config
    
    def add_bond(self, name: str, interfaces: List[str], mode: str = "active-backup",
                dhcp4: bool = True, dhcp6: bool = False, addresses: List[str] = None,
                gateway4: str = None, gateway6: str = None, 
                nameservers: List[str] = None) -> None:
        """Add bond interface configuration."""
        if "bonds" not in self.config["network"]:
            self.config["network"]["bonds"] = {}
        
        interface_config = {
            "interfaces": interfaces,
            "parameters": {"mode": mode}
        }
        
        if dhcp4:
            interface_config["dhcp4"] = True
        if dhcp6:
            interface_config["dhcp6"] = True
            
        if addresses:
            interface_config["addresses"] = addresses
            
        if gateway4:
            interface_config["gateway4"] = gateway4
        if gateway6:
            interface_config["gateway6"] = gateway6
            
        if nameservers:
            interface_config["nameservers"] = {"addresses": nameservers}
            
        self.config["network"]["bonds"][name] = interface_config
    
    def add_bridge(self, name: str, interfaces: List[str], dhcp4: bool = True, 
                  dhcp6: bool = False, addresses: List[str] = None,
                  gateway4: str = None, gateway6: str = None, 
                  nameservers: List[str] = None) -> None:
        """Add bridge interface configuration."""
        if "bridges" not in self.config["network"]:
            self.config["network"]["bridges"] = {}
        
        interface_config = {
            "interfaces": interfaces
        }
        
        if dhcp4:
            interface_config["dhcp4"] = True
        if dhcp6:
            interface_config["dhcp6"] = True
            
        if addresses:
            interface_config["addresses"] = addresses
            
        if gateway4:
            interface_config["gateway4"] = gateway4
        if gateway6:
            interface_config["gateway6"] = gateway6
            
        if nameservers:
            interface_config["nameservers"] = {"addresses": nameservers}
            
        self.config["network"]["bridges"][name] = interface_config
    
    def to_yaml(self) -> str:
        """Convert configuration to YAML string."""
        return yaml.dump(self.config, default_flow_style=False, sort_keys=False)


def parse_list(value: str) -> List[str]:
    """Parse comma-separated values into a list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",")]


def parse_overrides(value: str) -> Dict[str, Any]:
    """Parse key=value pairs into a dictionary."""
    if not value:
        return {}
    
    overrides = {}
    for pair in value.split(","):
        if "=" in pair:
            key, val = pair.split("=", 1)
            key = key.strip()
            val = val.strip()
            
            # Convert boolean and numeric values
            if val.lower() in ("true", "false"):
                val = val.lower() == "true"
            elif val.isdigit():
                val = int(val)
                
            overrides[key] = val
    
    return overrides


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate netplan YAML configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # DHCP ethernet interface
  python netplan_generator.py --ethernet eth0

  # Static ethernet interface
  python netplan_generator.py --ethernet eth0 --static --addresses 192.168.1.100/24 --gateway4 192.168.1.1

  # Bond interface
  python netplan_generator.py --bond bond0 --bond-interfaces eth0,eth1

  # Bridge interface
  python netplan_generator.py --bridge br0 --bridge-interfaces eth0,eth1

  # Output to file
  python netplan_generator.py --ethernet eth0 --output config.yaml
        """
    )
    
    # General options
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--renderer", default="networkd", 
                       choices=["networkd", "NetworkManager"],
                       help="Network renderer (default: networkd)")
    
    # Interface options
    parser.add_argument("--ethernet", help="Ethernet interface name")
    parser.add_argument("--bond", help="Bond interface name")
    parser.add_argument("--bridge", help="Bridge interface name")
    
    # Configuration options
    parser.add_argument("--static", action="store_true",
                       help="Use static configuration instead of DHCP")
    parser.add_argument("--addresses", help="Comma-separated IP addresses")
    parser.add_argument("--gateway4", help="IPv4 gateway")
    parser.add_argument("--gateway6", help="IPv6 gateway")
    parser.add_argument("--nameservers", help="Comma-separated nameservers")
    parser.add_argument("--dhcp4-overrides", help="DHCP4 overrides (key=value,key=value)")
    parser.add_argument("--dhcp6-overrides", help="DHCP6 overrides (key=value,key=value)")
    
    # Bond/Bridge specific options
    parser.add_argument("--bond-interfaces", help="Comma-separated interfaces for bond")
    parser.add_argument("--bond-mode", default="active-backup",
                       help="Bond mode (default: active-backup)")
    parser.add_argument("--bridge-interfaces", help="Comma-separated interfaces for bridge")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.ethernet, args.bond, args.bridge]):
        parser.error("At least one interface type must be specified")
    
    generator = NetplanGenerator(args.renderer)
    
    # Process ethernet interface
    if args.ethernet:
        addresses = parse_list(args.addresses) if args.addresses else None
        nameservers = parse_list(args.nameservers) if args.nameservers else None
        dhcp4_overrides = parse_overrides(args.dhcp4_overrides) if args.dhcp4_overrides else None
        dhcp6_overrides = parse_overrides(args.dhcp6_overrides) if args.dhcp6_overrides else None
        
        generator.add_ethernet(
            name=args.ethernet,
            dhcp4=not args.static,
            dhcp6=False,
            addresses=addresses,
            gateway4=args.gateway4,
            gateway6=args.gateway6,
            nameservers=nameservers,
            dhcp4_overrides=dhcp4_overrides,
            dhcp6_overrides=dhcp6_overrides
        )
    
    # Process bond interface
    if args.bond:
        if not args.bond_interfaces:
            parser.error("--bond-interfaces is required when using --bond")
        
        bond_interfaces = parse_list(args.bond_interfaces)
        addresses = parse_list(args.addresses) if args.addresses else None
        nameservers = parse_list(args.nameservers) if args.nameservers else None
        
        generator.add_bond(
            name=args.bond,
            interfaces=bond_interfaces,
            mode=args.bond_mode,
            dhcp4=not args.static,
            dhcp6=False,
            addresses=addresses,
            gateway4=args.gateway4,
            gateway6=args.gateway6,
            nameservers=nameservers
        )
    
    # Process bridge interface
    if args.bridge:
        if not args.bridge_interfaces:
            parser.error("--bridge-interfaces is required when using --bridge")
        
        bridge_interfaces = parse_list(args.bridge_interfaces)
        addresses = parse_list(args.addresses) if args.addresses else None
        nameservers = parse_list(args.nameservers) if args.nameservers else None
        
        generator.add_bridge(
            name=args.bridge,
            interfaces=bridge_interfaces,
            dhcp4=not args.static,
            dhcp6=False,
            addresses=addresses,
            gateway4=args.gateway4,
            gateway6=args.gateway6,
            nameservers=nameservers
        )
    
    # Generate YAML output
    yaml_output = generator.to_yaml()
    
    # Output to file or stdout
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(yaml_output)
            print(f"Configuration written to {args.output}")
        except IOError as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(yaml_output)


if __name__ == "__main__":
    main()