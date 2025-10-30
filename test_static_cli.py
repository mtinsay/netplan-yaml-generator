#!/usr/bin/env python3
"""
Test script to verify CLI behavior for --static without --addresses

Copyright (C) 2025 Michael Tinsay

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import subprocess
import sys
import os

def test_cli_static_without_addresses():
    """Test CLI behavior for --static without --addresses"""
    print("Testing CLI --static without --addresses...")
    
    # Test ethernet
    try:
        result = subprocess.run([
            sys.executable, "netplan_generator.py", 
            "--ethernet", "eth0", 
            "--static"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            output = result.stdout
            print("Ethernet static without addresses output:")
            print(output)
            
            if "dhcp4: false" in output or "dhcp4: no" in output:
                print("✓ Ethernet CLI test passed")
            else:
                print("❌ Ethernet CLI test failed - no dhcp4: false found")
                return False
        else:
            print(f"❌ Ethernet CLI test failed with error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ethernet CLI test failed with exception: {e}")
        return False
    
    # Test bond
    try:
        result = subprocess.run([
            sys.executable, "netplan_generator.py", 
            "--bond", "bond0", 
            "--bond-interfaces", "eth0,eth1",
            "--static"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            output = result.stdout
            print("\nBond static without addresses output:")
            print(output)
            
            if "dhcp4: false" in output or "dhcp4: no" in output:
                print("✓ Bond CLI test passed")
            else:
                print("❌ Bond CLI test failed - no dhcp4: false found")
                return False
        else:
            print(f"❌ Bond CLI test failed with error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Bond CLI test failed with exception: {e}")
        return False
    
    # Test bridge
    try:
        result = subprocess.run([
            sys.executable, "netplan_generator.py", 
            "--bridge", "br0", 
            "--bridge-interfaces", "eth0,eth1",
            "--static"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            output = result.stdout
            print("\nBridge static without addresses output:")
            print(output)
            
            if "dhcp4: false" in output or "dhcp4: no" in output:
                print("✓ Bridge CLI test passed")
            else:
                print("❌ Bridge CLI test failed - no dhcp4: false found")
                return False
        else:
            print(f"❌ Bridge CLI test failed with error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Bridge CLI test failed with exception: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing CLI --static without --addresses behavior\n")
    
    if test_cli_static_without_addresses():
        print("\n🎉 All CLI tests passed! --static without --addresses correctly sets dhcp4: false")
    else:
        print("\n❌ Some CLI tests failed!")
        sys.exit(1)