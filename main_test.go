/*
Netplan Web Generator Tests

Copyright (C) 2025 Michael Tinsay

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
*/

package main

import (
	"strings"
	"testing"
)

func TestParseCommaSeparated(t *testing.T) {
	tests := []struct {
		input    string
		expected []string
	}{
		{"", nil},
		{"eth0", []string{"eth0"}},
		{"eth0,eth1", []string{"eth0", "eth1"}},
		{"eth0, eth1, eth2", []string{"eth0", "eth1", "eth2"}},
		{" eth0 , eth1 ", []string{"eth0", "eth1"}},
	}

	for _, test := range tests {
		result := parseCommaSeparated(test.input)
		if len(result) != len(test.expected) {
			t.Errorf("parseCommaSeparated(%q) = %v, want %v", test.input, result, test.expected)
			continue
		}
		for i, v := range result {
			if v != test.expected[i] {
				t.Errorf("parseCommaSeparated(%q) = %v, want %v", test.input, result, test.expected)
				break
			}
		}
	}
}

func TestParseKeyValuePairs(t *testing.T) {
	tests := []struct {
		input    string
		expected map[string]interface{}
	}{
		{"", nil},
		{"key=value", map[string]interface{}{"key": "value"}},
		{"use-dns=false", map[string]interface{}{"use-dns": false}},
		{"timeout=30", map[string]interface{}{"timeout": 30}},
		{"key1=value1,key2=true,key3=42", map[string]interface{}{
			"key1": "value1",
			"key2": true,
			"key3": 42,
		}},
	}

	for _, test := range tests {
		result := parseKeyValuePairs(test.input)
		if len(result) != len(test.expected) {
			t.Errorf("parseKeyValuePairs(%q) length = %d, want %d", test.input, len(result), len(test.expected))
			continue
		}
		for k, v := range test.expected {
			if result[k] != v {
				t.Errorf("parseKeyValuePairs(%q)[%q] = %v, want %v", test.input, k, result[k], v)
			}
		}
	}
}

func TestGenerateEthernetConfig(t *testing.T) {
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: "networkd",
		},
	}

	formData := FormData{
		InterfaceName: "eth0",
		UseStatic:     false,
		Renderer:      "networkd",
	}

	result, err := generateEthernetConfig(config, formData)
	if err != nil {
		t.Fatalf("generateEthernetConfig failed: %v", err)
	}

	if len(result.Network.Ethernets) != 1 {
		t.Errorf("Expected 1 ethernet interface, got %d", len(result.Network.Ethernets))
	}

	eth, exists := result.Network.Ethernets["eth0"]
	if !exists {
		t.Errorf("Expected eth0 interface to exist")
	}

	if eth.DHCP4 == nil || !*eth.DHCP4 {
		t.Errorf("Expected DHCP4 to be true")
	}
}

func TestGenerateStaticEthernetConfig(t *testing.T) {
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: "networkd",
		},
	}

	formData := FormData{
		InterfaceName: "eth0",
		UseStatic:     true,
		Addresses:     "192.168.1.100/24",
		Gateway4:      "192.168.1.1",
		Nameservers:   "8.8.8.8,8.8.4.4",
		Renderer:      "networkd",
	}

	result, err := generateEthernetConfig(config, formData)
	if err != nil {
		t.Fatalf("generateEthernetConfig failed: %v", err)
	}

	eth := result.Network.Ethernets["eth0"]

	if len(eth.Addresses) != 1 || eth.Addresses[0] != "192.168.1.100/24" {
		t.Errorf("Expected address 192.168.1.100/24, got %v", eth.Addresses)
	}

	if eth.Gateway4 != "192.168.1.1" {
		t.Errorf("Expected gateway4 192.168.1.1, got %s", eth.Gateway4)
	}

	if eth.Nameservers == nil || len(eth.Nameservers.Addresses) != 2 {
		t.Errorf("Expected 2 nameservers, got %v", eth.Nameservers)
	}
}

func TestConfigToYAML(t *testing.T) {
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: "networkd",
			Ethernets: map[string]EthernetConfig{
				"eth0": {
					DHCP4: func() *bool { b := true; return &b }(),
				},
			},
		},
	}

	yaml := configToYAML(config)

	expectedStrings := []string{
		"network:",
		"version: 2",
		"renderer: networkd",
		"ethernets:",
		"eth0:",
		"dhcp4: true",
	}

	for _, expected := range expectedStrings {
		if !strings.Contains(yaml, expected) {
			t.Errorf("Expected YAML to contain %q, got:\n%s", expected, yaml)
		}
	}
}

func TestBondWithEthernetDeclarations(t *testing.T) {
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: "networkd",
		},
	}

	formData := FormData{
		InterfaceName:  "bond0",
		BondInterfaces: "eth0,eth1",
		BondMode:       "active-backup",
		UseStatic:      false,
		Renderer:       "networkd",
	}

	result, err := generateBondConfig(config, formData)
	if err != nil {
		t.Fatalf("generateBondConfig failed: %v", err)
	}

	yaml := configToYAML(result)

	// Check that YAML contains ethernet declarations with dhcp4: false
	expectedStrings := []string{
		"ethernets:",
		"eth0:",
		"dhcp4: false",
		"eth1:",
		"bonds:",
		"bond0:",
		"interfaces:",
		"- eth0",
		"- eth1",
		"parameters:",
		"mode: active-backup",
	}

	for _, expected := range expectedStrings {
		if !strings.Contains(yaml, expected) {
			t.Errorf("Expected YAML to contain %q, got:\n%s", expected, yaml)
		}
	}
}

func TestStaticWithoutAddresses(t *testing.T) {
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: "networkd",
		},
	}

	// Test ethernet static without addresses
	formData := FormData{
		InterfaceName: "eth0",
		UseStatic:     true,
		Renderer:      "networkd",
	}

	result, err := generateEthernetConfig(config, formData)
	if err != nil {
		t.Fatalf("generateEthernetConfig failed: %v", err)
	}

	yaml := configToYAML(result)

	// Should contain dhcp4: false when static is used without addresses
	if !strings.Contains(yaml, "dhcp4: false") {
		t.Errorf("Expected YAML to contain 'dhcp4: false' for static without addresses, got:\n%s", yaml)
	}
}

func TestGenerateBondConfig(t *testing.T) {
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: "networkd",
		},
	}

	formData := FormData{
		InterfaceName:  "bond0",
		BondInterfaces: "eth0,eth1",
		BondMode:       "active-backup",
		UseStatic:      false,
		Renderer:       "networkd",
	}

	result, err := generateBondConfig(config, formData)
	if err != nil {
		t.Fatalf("generateBondConfig failed: %v", err)
	}

	if len(result.Network.Bonds) != 1 {
		t.Errorf("Expected 1 bond interface, got %d", len(result.Network.Bonds))
	}

	bond, exists := result.Network.Bonds["bond0"]
	if !exists {
		t.Errorf("Expected bond0 interface to exist")
	}

	if len(bond.Interfaces) != 2 || bond.Interfaces[0] != "eth0" || bond.Interfaces[1] != "eth1" {
		t.Errorf("Expected interfaces [eth0, eth1], got %v", bond.Interfaces)
	}

	if bond.Parameters.Mode != "active-backup" {
		t.Errorf("Expected mode active-backup, got %s", bond.Parameters.Mode)
	}

	// Check that ethernet interfaces are declared with dhcp4: false
	if len(result.Network.Ethernets) != 2 {
		t.Errorf("Expected 2 ethernet interfaces, got %d", len(result.Network.Ethernets))
	}

	for _, ifaceName := range []string{"eth0", "eth1"} {
		eth, exists := result.Network.Ethernets[ifaceName]
		if !exists {
			t.Errorf("Expected ethernet interface %s to exist", ifaceName)
		}
		if eth.DHCP4 == nil || *eth.DHCP4 != false {
			t.Errorf("Expected ethernet interface %s to have dhcp4: false", ifaceName)
		}
	}
}

func TestGenerateBridgeConfig(t *testing.T) {
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: "networkd",
		},
	}

	formData := FormData{
		InterfaceName:    "br0",
		BridgeInterfaces: "eth0,eth1",
		UseStatic:        false,
		Renderer:         "networkd",
	}

	result, err := generateBridgeConfig(config, formData)
	if err != nil {
		t.Fatalf("generateBridgeConfig failed: %v", err)
	}

	if len(result.Network.Bridges) != 1 {
		t.Errorf("Expected 1 bridge interface, got %d", len(result.Network.Bridges))
	}

	bridge, exists := result.Network.Bridges["br0"]
	if !exists {
		t.Errorf("Expected br0 interface to exist")
	}

	if len(bridge.Interfaces) != 2 || bridge.Interfaces[0] != "eth0" || bridge.Interfaces[1] != "eth1" {
		t.Errorf("Expected interfaces [eth0, eth1], got %v", bridge.Interfaces)
	}

	// Check that ethernet interfaces are declared with dhcp4: false
	if len(result.Network.Ethernets) != 2 {
		t.Errorf("Expected 2 ethernet interfaces, got %d", len(result.Network.Ethernets))
	}

	for _, ifaceName := range []string{"eth0", "eth1"} {
		eth, exists := result.Network.Ethernets[ifaceName]
		if !exists {
			t.Errorf("Expected ethernet interface %s to exist", ifaceName)
		}
		if eth.DHCP4 == nil || *eth.DHCP4 != false {
			t.Errorf("Expected ethernet interface %s to have dhcp4: false", ifaceName)
		}
	}
}