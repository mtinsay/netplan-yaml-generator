# Netplan Web Generator

A standalone Go web application for generating netplan YAML configurations through a user-friendly web interface.

## Features

- **Web-based Interface**: Single-page application with intuitive form controls
- **Real-time Generation**: Instant YAML output as you configure
- **All Interface Types**: Support for ethernet, bond, and bridge interfaces
- **DHCP & Static**: Both DHCP and static IP configuration options
- **DHCP Overrides**: Custom DHCP client behavior configuration
- **Responsive Design**: Works on desktop and mobile devices
- **Copy to Clipboard**: Easy copying of generated YAML
- **Containerized**: Ready for Docker deployment
- **No Dependencies**: Uses only Go standard library

## Quick Start

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd netplan-web-generator

# Run the application
go run main.go

# Open your browser
open http://localhost:8080
```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t netplan-web-generator .
docker run -p 8080:8080 netplan-web-generator

# Or use docker-compose
docker-compose up -d
```

### Production Deployment

```bash
# Build for production
CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o netplan-generator .

# Run the binary
./netplan-generator
```

## Configuration

The application can be configured using environment variables:

- `PORT`: Server port (default: 8080)

## Interface Types

### Ethernet Interfaces
- DHCP or static IP configuration
- Gateway and nameserver settings
- DHCP override options
- IPv4 and IPv6 support

### Bond Interfaces
- Multiple bonding modes:
  - `active-backup` (default)
  - `balance-rr`
  - `balance-xor`
  - `broadcast`
  - `802.3ad`
  - `balance-tlb`
  - `balance-alb`
- Interface aggregation
- High availability configuration

### Bridge Interfaces
- Virtual bridge creation
- Interface bridging
- VM and container networking

## Web Interface

The web application provides:

1. **Configuration Form**:
   - Interface type selection
   - Dynamic form fields based on interface type
   - Static/DHCP toggle
   - Validation and error handling

2. **YAML Output**:
   - Real-time generation
   - Syntax-highlighted display
   - Copy to clipboard functionality
   - Proper netplan formatting

3. **Responsive Design**:
   - Mobile-friendly interface
   - Grid-based layout
   - Modern CSS styling

## API Endpoints

- `GET /`: Main web interface
- `POST /generate`: Generate netplan configuration

## Docker

### Building the Image

```bash
docker build -t netplan-web-generator .
```

### Running the Container

```bash
# Basic run
docker run -p 8080:8080 netplan-web-generator

# With custom port
docker run -p 3000:3000 -e PORT=3000 netplan-web-generator

# With docker-compose
docker-compose up -d
```

### Health Checks

The container includes health checks that verify the application is responding correctly.

## Examples

### DHCP Ethernet Interface
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
```

### Static Ethernet Interface
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

### Bond Interface
```yaml
network:
  version: 2
  renderer: networkd
  bonds:
    bond0:
      interfaces:
        - eth0
        - eth1
      parameters:
        mode: active-backup
      dhcp4: true
```

### Bridge Interface
```yaml
network:
  version: 2
  renderer: networkd
  bridges:
    br0:
      interfaces:
        - eth0
        - eth1
      dhcp4: true
```

## Development

### Project Structure
```
.
├── main.go              # Main application
├── templates/
│   └── index.html       # Web interface template
├── go.mod               # Go module file
├── Dockerfile           # Container build file
├── docker-compose.yml   # Docker Compose configuration
└── README-web.md        # This file
```

### Building

```bash
# Local build
go build -o netplan-generator

# Cross-platform builds
GOOS=linux GOARCH=amd64 go build -o netplan-generator-linux-amd64
GOOS=windows GOARCH=amd64 go build -o netplan-generator-windows-amd64.exe
GOOS=darwin GOARCH=amd64 go build -o netplan-generator-darwin-amd64
```

### Testing

```bash
# Test the web interface
curl -X POST http://localhost:8080/generate \
  -d "interface_type=ethernet&interface_name=eth0&renderer=networkd"
```

## Security

- Runs as non-root user in container
- Input validation and sanitization
- No external dependencies
- Minimal attack surface

## Performance

- Lightweight Go binary (~10MB)
- Fast startup time
- Low memory footprint
- Efficient template rendering

## License

Copyright (C) 2025 Michael Tinsay

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check existing issues
2. Create a new issue with detailed information
3. Include steps to reproduce any bugs