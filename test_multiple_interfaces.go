/*
Test for multiple interface functionality

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

func TestMultipleEthernetInterfaces(t *testing.T) {
	formData := FormData{
		Interfaces: []InterfaceDefinition{
			{
				Type:      "ethernet",
				Name:      "eth0",
				UseStatic: false,
			},
			{
				Type:      "ethernet",
				Name:      "eth1",
				UseStatic: true,
				Addresses: "192.168.1.100/24",
				Gateway4:  "192.168.1.1",
			},
		},
		Renderer: "networkd",
	}

	config, err := generateNetplanConfig(formData)
	if err != nil {
		t.Fatalf("generateNetplanConfig failed: %v", err)
	}

	yaml := configToYAML(config)

	// Check that both ethernet interfaces are present
	expectedStrings := []string{
		"ethernets:",
		"eth0:",
		"dhcp4: true",
		"eth1:",
		"dhcp4: false",
		"addresses:",
		"- 192.168.1.100/24",
		"gateway4: 192.168.1.1",
	}

	for _, expected := range expectedStrings {
		if !strings.Contains(yaml, expected) {
			t.Errorf("Expected YAML to contain %q, got:\n%s", expected, yaml)
		}
	}
}

func TestBondAndBridge(t *testing.T) {
	formData := FormData{
		Interfaces: []InterfaceDefinition{
			{
				Type:           "bond",
				Name:           "bond0",
				BondInterfaces: "eth0,eth1",
				BondMode:       "active-backup",
				UseStatic:      false,
			},
			{
				Type:             "bridge",
				Name:             "br0",
				BridgeInterfaces: "bond0",
				UseStatic:        true,
				Addresses:        "192.168.100.1/24",
			},
		},
		Renderer: "networkd",
	}

	config, err := generateNetplanConfig(formData)
	if err != nil {
		t.Fatalf("generateNetplanConfig failed: %v", err)
	}

	yaml := configToYAML(config)

	// Check that we have ethernet declarations for bond interfaces
	// but not for the bond itself when used in bridge
	expectedStrings := []string{
		"ethernets:",
		"eth0:",
		"dhcp4: false",
		"eth1:",
		"dhcp4: false",
		"bonds:",
		"bond0:",
		"interfaces:",
		"- eth0",
		"- eth1",
		"parameters:",
		"mode: active-backup",
		"bridges:",
		"br0:",
		"- bond0",
		"addresses:",
		"- 192.168.100.1/24",
	}

	for _, expected := range expectedStrings {
		if !strings.Contains(yaml, expected) {
			t.Errorf("Expected YAML to contain %q, got:\n%s", expected, yaml)
		}
	}

	// Verify that bond0 is NOT in ethernets section (since it's a bond, not ethernet)
	lines := strings.Split(yaml, "\n")
	inEthernets := false
	for _, line := range lines {
		if strings.Contains(line, "ethernets:") {
			inEthernets = true
			continue
		}
		if strings.Contains(line, "bonds:") || strings.Contains(line, "bridges:") {
			inEthernets = false
			continue
		}
		if inEthernets && strings.Contains(line, "bond0:") {
			t.Errorf("bond0 should not appear in ethernets section, got:\n%s", yaml)
		}
	}
}

func TestComplexConfiguration(t *testing.T) {
	formData := FormData{
		Interfaces: []InterfaceDefinition{
			{
				Type:      "ethernet",
				Name:      "eth0",
				UseStatic: false,
			},
			{
				Type:           "bond",
				Name:           "bond0",
				BondInterfaces: "eth1,eth2",
				BondMode:       "802.3ad",
				UseStatic:      true,
				Addresses:      "10.0.1.100/24",
				Gateway4:       "10.0.1.1",
			},
			{
				Type:             "bridge",
				Name:             "br0",
				BridgeInterfaces: "eth3,bond0",
				UseStatic:        true,
				Addresses:        "192.168.100.1/24",
			},
		},
		Renderer: "networkd",
	}

	config, err := generateNetplanConfig(formData)
	if err != nil {
		t.Fatalf("generateNetplanConfig failed: %v", err)
	}

	yaml := configToYAML(config)

	// Verify all sections exist
	if !strings.Contains(yaml, "ethernets:") {
		t.Error("Expected ethernets section")
	}
	if !strings.Contains(yaml, "bonds:") {
		t.Error("Expected bonds section")
	}
	if !strings.Contains(yaml, "bridges:") {
		t.Error("Expected bridges section")
	}

	// Verify ethernet interfaces
	ethernetInterfaces := []string{"eth0", "eth1", "eth2", "eth3"}
	for _, iface := range ethernetInterfaces {
		if !strings.Contains(yaml, iface+":") {
			t.Errorf("Expected ethernet interface %s", iface)
		}
	}

	// Verify bond configuration
	if !strings.Contains(yaml, "bond0:") {
		t.Error("Expected bond0 interface")
	}
	if !strings.Contains(yaml, "mode: 802.3ad") {
		t.Error("Expected bond mode 802.3ad")
	}

	// Verify bridge configuration
	if !strings.Contains(yaml, "br0:") {
		t.Error("Expected br0 interface")
	}
	if !strings.Contains(yaml, "- eth3") {
		t.Error("Expected eth3 in bridge interfaces")
	}
	if !strings.Contains(yaml, "- bond0") {
		t.Error("Expected bond0 in bridge interfaces")
	}
}