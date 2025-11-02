#!/usr/bin/env python3
"""
Test script for NetworkManager configuration generation

Copyright (C) 2025 Michael Tinsay

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import subprocess
import sys
import os
from netplan_generator import generate_networkmanager_config

def test_networkmanager_function():
    """Test the generate_networkmanager_config function directly"""
    print("Testing generate_networkmanager_config() function...")
    
    yaml_output = generate_networkmanager_config()
    
    print("Generated NetworkManager configuration:")
    print("=" * 50)
    print(yaml_output)
    print("=" * 50)
    
    # Verify basic structure
    assert "network:" in yaml_output, "Should contain network section"
    assert "version: 2" in yaml_output, "Should contain version 2"
    assert "renderer: NetworkManager" in yaml_output, "Should use NetworkManager renderer"
    
    # Verify comments are present
    assert "nmcli" in yaml_output, "Should contain nmcli information"
    assert "nm-connection-editor" in yaml_output, "Should contain GUI tool information"
    assert "NetworkManager command-line interface" in yaml_output, "Should contain CLI description"
    assert "man nmcli" in yaml_output, "Should contain manual page reference"
    assert "https://networkmanager.dev/" in yaml_output, "Should contain documentation URL"
    
    print("✓ Function test passed")

def test_networkmanager_cli():
    """Test the --use-nm CLI parameter"""
    print("\nTesting --use-nm CLI parameter...")
    
    try:
        result = subprocess.run([
            sys.executable, "netplan_generator.py", 
            "--use-nm"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            output = result.stdout
            print("CLI output:")
            print("=" * 30)
            print(output)
            print("=" * 30)
            
            # Verify basic structure
            assert "network:" in output, "CLI should contain network section"
            assert "version: 2" in output, "CLI should contain version 2"
            assert "renderer: NetworkManager" in output, "CLI should use NetworkManager renderer"
            assert "nmcli" in output, "CLI should contain nmcli information"
            
            print("✓ CLI test passed")
            return True
        else:
            print(f"❌ CLI test failed with error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed with exception: {e}")
        return False

def test_use_nm_ignores_other_params():
    """Test that --use-nm ignores other parameters"""
    print("\nTesting that --use-nm ignores other parameters...")
    
    try:
        # Run with --use-nm and other parameters that should be ignored
        result = subprocess.run([
            sys.executable, "netplan_generator.py", 
            "--use-nm",
            "--ethernet", "eth0",
            "--static",
            "--addresses", "192.168.1.100/24"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            output = result.stdout
            
            # Should only contain NetworkManager config, not ethernet config
            assert "renderer: NetworkManager" in output, "Should use NetworkManager renderer"
            assert "eth0:" not in output, "Should not contain ethernet interface config"
            assert "192.168.1.100" not in output, "Should not contain static IP config"
            assert "nmcli" in output, "Should contain NetworkManager comments"
            
            print("✓ Parameter ignore test passed")
            return True
        else:
            print(f"❌ Parameter ignore test failed with error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Parameter ignore test failed with exception: {e}")
        return False

def test_use_nm_with_output_file():
    """Test --use-nm with output file"""
    print("\nTesting --use-nm with output file...")
    
    output_file = "test_nm_config.yaml"
    
    try:
        # Clean up any existing file
        if os.path.exists(output_file):
            os.remove(output_file)
        
        result = subprocess.run([
            sys.executable, "netplan_generator.py", 
            "--use-nm",
            "--output", output_file
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            # Check that file was created
            assert os.path.exists(output_file), "Output file should be created"
            
            # Read and verify file content
            with open(output_file, 'r') as f:
                content = f.read()
            
            assert "renderer: NetworkManager" in content, "File should contain NetworkManager config"
            assert "nmcli" in content, "File should contain NetworkManager comments"
            
            print("✓ Output file test passed")
            
            # Clean up
            os.remove(output_file)
            return True
        else:
            print(f"❌ Output file test failed with error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Output file test failed with exception: {e}")
        return False
    finally:
        # Clean up in case of error
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == "__main__":
    print("Testing NetworkManager configuration functionality\n")
    
    success = True
    
    try:
        test_networkmanager_function()
        
        if not test_networkmanager_cli():
            success = False
            
        if not test_use_nm_ignores_other_params():
            success = False
            
        if not test_use_nm_with_output_file():
            success = False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        success = False
    
    if success:
        print("\n🎉 All NetworkManager tests passed!")
        print("The --use-nm parameter works correctly and generates proper NetworkManager configuration.")
    else:
        print("\n❌ Some NetworkManager tests failed!")
        sys.exit(1)