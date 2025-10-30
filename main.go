/*
Netplan Web Generator

A standalone Go web application for generating netplan YAML configurations
through a user-friendly web interface.

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
*/

package main

import (
	"embed"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
)

//go:embed templates/*
var templateFS embed.FS

// NetplanConfig represents the netplan configuration structure
type NetplanConfig struct {
	Network NetworkConfig `yaml:"network"`
}

type NetworkConfig struct {
	Version   int                       `yaml:"version"`
	Renderer  string                    `yaml:"renderer"`
	Ethernets map[string]EthernetConfig `yaml:"ethernets,omitempty"`
	Bonds     map[string]BondConfig     `yaml:"bonds,omitempty"`
	Bridges   map[string]BridgeConfig   `yaml:"bridges,omitempty"`
}

type EthernetConfig struct {
	DHCP4           *bool                  `yaml:"dhcp4,omitempty"`
	DHCP6           *bool                  `yaml:"dhcp6,omitempty"`
	Addresses       []string               `yaml:"addresses,omitempty"`
	Gateway4        string                 `yaml:"gateway4,omitempty"`
	Gateway6        string                 `yaml:"gateway6,omitempty"`
	Nameservers     *NameserversConfig     `yaml:"nameservers,omitempty"`
	DHCP4Overrides  map[string]interface{} `yaml:"dhcp4-overrides,omitempty"`
	DHCP6Overrides  map[string]interface{} `yaml:"dhcp6-overrides,omitempty"`
}

type BondConfig struct {
	Interfaces  []string           `yaml:"interfaces"`
	Parameters  BondParameters     `yaml:"parameters"`
	DHCP4       *bool              `yaml:"dhcp4,omitempty"`
	DHCP6       *bool              `yaml:"dhcp6,omitempty"`
	Addresses   []string           `yaml:"addresses,omitempty"`
	Gateway4    string             `yaml:"gateway4,omitempty"`
	Gateway6    string             `yaml:"gateway6,omitempty"`
	Nameservers *NameserversConfig `yaml:"nameservers,omitempty"`
}

type BridgeConfig struct {
	Interfaces  []string           `yaml:"interfaces"`
	DHCP4       *bool              `yaml:"dhcp4,omitempty"`
	DHCP6       *bool              `yaml:"dhcp6,omitempty"`
	Addresses   []string           `yaml:"addresses,omitempty"`
	Gateway4    string             `yaml:"gateway4,omitempty"`
	Gateway6    string             `yaml:"gateway6,omitempty"`
	Nameservers *NameserversConfig `yaml:"nameservers,omitempty"`
}

type BondParameters struct {
	Mode string `yaml:"mode"`
}

type NameserversConfig struct {
	Addresses []string `yaml:"addresses"`
}

// FormData represents the web form input
type FormData struct {
	InterfaceType    string
	InterfaceName    string
	UseStatic        bool
	Addresses        string
	Gateway4         string
	Gateway6         string
	Nameservers      string
	DHCP4Overrides   string
	DHCP6Overrides   string
	BondInterfaces   string
	BondMode         string
	BridgeInterfaces string
	Renderer         string
}

// PageData represents data passed to the template
type PageData struct {
	FormData FormData
	Output   string
	Error    string
}

func main() {
	http.HandleFunc("/", handleIndex)
	http.HandleFunc("/generate", handleGenerate)
	http.HandleFunc("/version", handleVersion)
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	
	log.Printf("Netplan Web Generator v1.0.0")
	log.Printf("Copyright (C) 2025 Michael Tinsay")
	log.Printf("Licensed under GPLv3 - https://www.gnu.org/licenses/gpl-3.0.html")
	log.Printf("Starting server on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func handleIndex(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFS(templateFS, "templates/index.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	data := PageData{
		FormData: FormData{
			Renderer: "networkd",
			BondMode: "active-backup",
		},
	}
	
	tmpl.Execute(w, data)
}

func handleVersion(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	version := `{
		"name": "Netplan Web Generator",
		"version": "1.0.0",
		"copyright": "Copyright (C) 2025 Michael Tinsay",
		"license": "GPLv3",
		"license_url": "https://www.gnu.org/licenses/gpl-3.0.html",
		"description": "A standalone Go web application for generating netplan YAML configurations",
		"repository": "https://github.com/mtinsay/netplan-yaml-generator"
	}`
	w.Write([]byte(version))
}

func handleGenerate(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}
	
	// Parse form data
	formData := FormData{
		InterfaceType:    r.FormValue("interface_type"),
		InterfaceName:    r.FormValue("interface_name"),
		UseStatic:        r.FormValue("use_static") == "on",
		Addresses:        r.FormValue("addresses"),
		Gateway4:         r.FormValue("gateway4"),
		Gateway6:         r.FormValue("gateway6"),
		Nameservers:      r.FormValue("nameservers"),
		DHCP4Overrides:   r.FormValue("dhcp4_overrides"),
		DHCP6Overrides:   r.FormValue("dhcp6_overrides"),
		BondInterfaces:   r.FormValue("bond_interfaces"),
		BondMode:         r.FormValue("bond_mode"),
		BridgeInterfaces: r.FormValue("bridge_interfaces"),
		Renderer:         r.FormValue("renderer"),
	}
	
	// Generate netplan configuration
	config, err := generateNetplanConfig(formData)
	if err != nil {
		renderPage(w, formData, "", err.Error())
		return
	}
	
	// Convert to YAML
	yamlOutput := configToYAML(config)
	
	renderPage(w, formData, yamlOutput, "")
}

func renderPage(w http.ResponseWriter, formData FormData, output, errorMsg string) {
	tmpl, err := template.ParseFS(templateFS, "templates/index.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	data := PageData{
		FormData: formData,
		Output:   output,
		Error:    errorMsg,
	}
	
	tmpl.Execute(w, data)
}

func generateNetplanConfig(formData FormData) (*NetplanConfig, error) {
	if formData.InterfaceName == "" {
		return nil, fmt.Errorf("interface name is required")
	}
	
	config := &NetplanConfig{
		Network: NetworkConfig{
			Version:  2,
			Renderer: formData.Renderer,
		},
	}
	
	switch formData.InterfaceType {
	case "ethernet":
		return generateEthernetConfig(config, formData)
	case "bond":
		return generateBondConfig(config, formData)
	case "bridge":
		return generateBridgeConfig(config, formData)
	default:
		return nil, fmt.Errorf("invalid interface type: %s", formData.InterfaceType)
	}
}

func generateEthernetConfig(config *NetplanConfig, formData FormData) (*NetplanConfig, error) {
	config.Network.Ethernets = make(map[string]EthernetConfig)
	
	ethConfig := EthernetConfig{}
	
	// Set DHCP or static configuration
	if !formData.UseStatic {
		dhcp4 := true
		ethConfig.DHCP4 = &dhcp4
	} else {
		// When static is selected, explicitly set dhcp4: false
		dhcp4 := false
		ethConfig.DHCP4 = &dhcp4
	}
	
	// Parse addresses
	if formData.Addresses != "" {
		ethConfig.Addresses = parseCommaSeparated(formData.Addresses)
	}
	
	// Set gateways
	if formData.Gateway4 != "" {
		ethConfig.Gateway4 = formData.Gateway4
	}
	if formData.Gateway6 != "" {
		ethConfig.Gateway6 = formData.Gateway6
	}
	
	// Parse nameservers
	if formData.Nameservers != "" {
		nameservers := parseCommaSeparated(formData.Nameservers)
		ethConfig.Nameservers = &NameserversConfig{Addresses: nameservers}
	}
	
	// Parse DHCP overrides
	if formData.DHCP4Overrides != "" {
		ethConfig.DHCP4Overrides = parseKeyValuePairs(formData.DHCP4Overrides)
	}
	if formData.DHCP6Overrides != "" {
		ethConfig.DHCP6Overrides = parseKeyValuePairs(formData.DHCP6Overrides)
	}
	
	config.Network.Ethernets[formData.InterfaceName] = ethConfig
	return config, nil
}

func generateBondConfig(config *NetplanConfig, formData FormData) (*NetplanConfig, error) {
	if formData.BondInterfaces == "" {
		return nil, fmt.Errorf("bond interfaces are required")
	}
	
	bondInterfaces := parseCommaSeparated(formData.BondInterfaces)
	
	// Initialize ethernets map if it doesn't exist
	if config.Network.Ethernets == nil {
		config.Network.Ethernets = make(map[string]EthernetConfig)
	}
	
	// Add ethernet declarations for bond interfaces with dhcp4: false
	for _, iface := range bondInterfaces {
		dhcp4 := false
		config.Network.Ethernets[iface] = EthernetConfig{
			DHCP4: &dhcp4,
		}
	}
	
	config.Network.Bonds = make(map[string]BondConfig)
	
	bondConfig := BondConfig{
		Interfaces: bondInterfaces,
		Parameters: BondParameters{Mode: formData.BondMode},
	}
	
	// Set DHCP or static configuration
	if !formData.UseStatic {
		dhcp4 := true
		bondConfig.DHCP4 = &dhcp4
	} else {
		// When static is selected, explicitly set dhcp4: false
		dhcp4 := false
		bondConfig.DHCP4 = &dhcp4
	}
	
	// Parse addresses
	if formData.Addresses != "" {
		bondConfig.Addresses = parseCommaSeparated(formData.Addresses)
	}
	
	// Set gateways
	if formData.Gateway4 != "" {
		bondConfig.Gateway4 = formData.Gateway4
	}
	if formData.Gateway6 != "" {
		bondConfig.Gateway6 = formData.Gateway6
	}
	
	// Parse nameservers
	if formData.Nameservers != "" {
		nameservers := parseCommaSeparated(formData.Nameservers)
		bondConfig.Nameservers = &NameserversConfig{Addresses: nameservers}
	}
	
	config.Network.Bonds[formData.InterfaceName] = bondConfig
	return config, nil
}

func generateBridgeConfig(config *NetplanConfig, formData FormData) (*NetplanConfig, error) {
	if formData.BridgeInterfaces == "" {
		return nil, fmt.Errorf("bridge interfaces are required")
	}
	
	bridgeInterfaces := parseCommaSeparated(formData.BridgeInterfaces)
	
	// Initialize ethernets map if it doesn't exist
	if config.Network.Ethernets == nil {
		config.Network.Ethernets = make(map[string]EthernetConfig)
	}
	
	// Add ethernet declarations for bridge interfaces with dhcp4: false
	for _, iface := range bridgeInterfaces {
		dhcp4 := false
		config.Network.Ethernets[iface] = EthernetConfig{
			DHCP4: &dhcp4,
		}
	}
	
	config.Network.Bridges = make(map[string]BridgeConfig)
	
	bridgeConfig := BridgeConfig{
		Interfaces: bridgeInterfaces,
	}
	
	// Set DHCP or static configuration
	if !formData.UseStatic {
		dhcp4 := true
		bridgeConfig.DHCP4 = &dhcp4
	} else {
		// When static is selected, explicitly set dhcp4: false
		dhcp4 := false
		bridgeConfig.DHCP4 = &dhcp4
	}
	
	// Parse addresses
	if formData.Addresses != "" {
		bridgeConfig.Addresses = parseCommaSeparated(formData.Addresses)
	}
	
	// Set gateways
	if formData.Gateway4 != "" {
		bridgeConfig.Gateway4 = formData.Gateway4
	}
	if formData.Gateway6 != "" {
		bridgeConfig.Gateway6 = formData.Gateway6
	}
	
	// Parse nameservers
	if formData.Nameservers != "" {
		nameservers := parseCommaSeparated(formData.Nameservers)
		bridgeConfig.Nameservers = &NameserversConfig{Addresses: nameservers}
	}
	
	config.Network.Bridges[formData.InterfaceName] = bridgeConfig
	return config, nil
}

func parseCommaSeparated(input string) []string {
	if input == "" {
		return nil
	}
	
	parts := strings.Split(input, ",")
	result := make([]string, 0, len(parts))
	for _, part := range parts {
		trimmed := strings.TrimSpace(part)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

func parseKeyValuePairs(input string) map[string]interface{} {
	if input == "" {
		return nil
	}
	
	result := make(map[string]interface{})
	pairs := strings.Split(input, ",")
	
	for _, pair := range pairs {
		parts := strings.SplitN(strings.TrimSpace(pair), "=", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])
			
			// Try to convert to appropriate type
			if value == "true" || value == "false" {
				result[key] = value == "true"
			} else if intVal, err := strconv.Atoi(value); err == nil {
				result[key] = intVal
			} else {
				result[key] = value
			}
		}
	}
	
	return result
}

func configToYAML(config *NetplanConfig) string {
	var sb strings.Builder
	
	sb.WriteString("network:\n")
	sb.WriteString(fmt.Sprintf("  version: %d\n", config.Network.Version))
	sb.WriteString(fmt.Sprintf("  renderer: %s\n", config.Network.Renderer))
	
	// Ethernet interfaces
	if len(config.Network.Ethernets) > 0 {
		sb.WriteString("  ethernets:\n")
		for name, eth := range config.Network.Ethernets {
			sb.WriteString(fmt.Sprintf("    %s:\n", name))
			writeInterfaceConfig(&sb, eth.DHCP4, eth.DHCP6, eth.Addresses, eth.Gateway4, eth.Gateway6, eth.Nameservers, eth.DHCP4Overrides, eth.DHCP6Overrides)
		}
	}
	
	// Bond interfaces
	if len(config.Network.Bonds) > 0 {
		sb.WriteString("  bonds:\n")
		for name, bond := range config.Network.Bonds {
			sb.WriteString(fmt.Sprintf("    %s:\n", name))
			sb.WriteString("      interfaces:\n")
			for _, iface := range bond.Interfaces {
				sb.WriteString(fmt.Sprintf("        - %s\n", iface))
			}
			sb.WriteString("      parameters:\n")
			sb.WriteString(fmt.Sprintf("        mode: %s\n", bond.Parameters.Mode))
			writeInterfaceConfig(&sb, bond.DHCP4, bond.DHCP6, bond.Addresses, bond.Gateway4, bond.Gateway6, bond.Nameservers, nil, nil)
		}
	}
	
	// Bridge interfaces
	if len(config.Network.Bridges) > 0 {
		sb.WriteString("  bridges:\n")
		for name, bridge := range config.Network.Bridges {
			sb.WriteString(fmt.Sprintf("    %s:\n", name))
			sb.WriteString("      interfaces:\n")
			for _, iface := range bridge.Interfaces {
				sb.WriteString(fmt.Sprintf("        - %s\n", iface))
			}
			writeInterfaceConfig(&sb, bridge.DHCP4, bridge.DHCP6, bridge.Addresses, bridge.Gateway4, bridge.Gateway6, bridge.Nameservers, nil, nil)
		}
	}
	
	return sb.String()
}

func writeInterfaceConfig(sb *strings.Builder, dhcp4, dhcp6 *bool, addresses []string, gateway4, gateway6 string, nameservers *NameserversConfig, dhcp4Overrides, dhcp6Overrides map[string]interface{}) {
	if dhcp4 != nil && *dhcp4 {
		sb.WriteString("      dhcp4: true\n")
	}
	if dhcp6 != nil && *dhcp6 {
		sb.WriteString("      dhcp6: true\n")
	}
	
	if len(addresses) > 0 {
		sb.WriteString("      addresses:\n")
		for _, addr := range addresses {
			sb.WriteString(fmt.Sprintf("        - %s\n", addr))
		}
	}
	
	if gateway4 != "" {
		sb.WriteString(fmt.Sprintf("      gateway4: %s\n", gateway4))
	}
	if gateway6 != "" {
		sb.WriteString(fmt.Sprintf("      gateway6: %s\n", gateway6))
	}
	
	if nameservers != nil && len(nameservers.Addresses) > 0 {
		sb.WriteString("      nameservers:\n")
		sb.WriteString("        addresses:\n")
		for _, ns := range nameservers.Addresses {
			sb.WriteString(fmt.Sprintf("          - %s\n", ns))
		}
	}
	
	if len(dhcp4Overrides) > 0 {
		sb.WriteString("      dhcp4-overrides:\n")
		for key, value := range dhcp4Overrides {
			sb.WriteString(fmt.Sprintf("        %s: %v\n", key, formatYAMLValue(value)))
		}
	}
	
	if len(dhcp6Overrides) > 0 {
		sb.WriteString("      dhcp6-overrides:\n")
		for key, value := range dhcp6Overrides {
			sb.WriteString(fmt.Sprintf("        %s: %v\n", key, formatYAMLValue(value)))
		}
	}
}

func formatYAMLValue(value interface{}) string {
	switch v := value.(type) {
	case bool:
		if v {
			return "true"
		}
		return "false"
	case string:
		return v
	default:
		return fmt.Sprintf("%v", v)
	}
}