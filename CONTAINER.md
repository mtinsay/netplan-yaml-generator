# Netplan Web Generator - Container Guide

This guide covers building and deploying the Netplan Web Generator as a container.

## 🐳 Container Overview

The container includes **only** the Go web application binary (`netplan-generator`) and excludes all Python files. It's optimized for production deployment with:

- **Minimal Alpine Linux base** (~15MB total image size)
- **Non-root user** for security
- **Health checks** for monitoring
- **Multi-architecture support** (amd64)
- **Static binary** with no external dependencies

## 📦 What's Included

### ✅ Included in Container
- `netplan-generator` (Go binary)
- `templates/index.html` (embedded in binary)
- SSL certificates for HTTPS
- Minimal Alpine Linux runtime

### ❌ Excluded from Container
- `netplan_generator.py` (Python CLI tool)
- `test_simple.py`, `test_generator.py` (Python tests)
- `examples.py` (Python examples)
- `requirements.txt` (Python dependencies)
- Development files (`.git`, `.vscode`, etc.)
- Documentation files (README files)

## 🚀 Quick Start

### Option 1: Docker Build

```bash
# Build the container
docker build -t netplan-web-generator .

# Run the container
docker run -p 8080:8080 netplan-web-generator

# Access the web application
open http://localhost:8080
```

### Option 2: Docker Compose

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Using Makefile

```bash
# Build and test
make docker-test

# Build and run
make docker-run

# Clean up
make docker-clean
```

## 🔧 Build Options

### Standard Build

```bash
docker build -t netplan-web-generator:latest .
```

### Optimized Build with Script

```bash
# Use the build script for comprehensive building and testing
bash build-container.sh
```

### Multi-platform Build

```bash
# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t netplan-web-generator:latest .
```

## 🏃 Running the Container

### Basic Run

```bash
docker run -d \
  --name netplan-generator \
  -p 8080:8080 \
  netplan-web-generator:latest
```

### Production Run

```bash
docker run -d \
  --name netplan-generator-prod \
  -p 8080:8080 \
  --restart unless-stopped \
  --read-only \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  netplan-web-generator:latest
```

### With Custom Port

```bash
docker run -d \
  --name netplan-generator \
  -p 3000:3000 \
  -e PORT=3000 \
  netplan-web-generator:latest
```

### With Volume Mounting (if needed)

```bash
# Note: The application doesn't require volumes, but you can mount config if needed
docker run -d \
  --name netplan-generator \
  -p 8080:8080 \
  -v /path/to/config:/app/config:ro \
  netplan-web-generator:latest
```

## 🔍 Container Information

### Image Details

```bash
# Check image size
docker images netplan-web-generator

# Inspect image
docker inspect netplan-web-generator:latest

# View image layers
docker history netplan-web-generator:latest
```

### Runtime Information

```bash
# Check running containers
docker ps

# View logs
docker logs netplan-generator

# Execute commands in container
docker exec -it netplan-generator /bin/sh
```

## 🏥 Health Checks

The container includes built-in health checks:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' netplan-generator

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' netplan-generator
```

Health check endpoint: `http://localhost:8080/`

## 🌐 Docker Compose Configurations

### Development (docker-compose.yml)

```yaml
version: '3.8'
services:
  netplan-web-generator:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
    restart: unless-stopped
```

### Production (docker-compose.prod.yml)

```yaml
version: '3.8'
services:
  netplan-web-generator:
    image: netplan-web-generator:1.0.0
    ports:
      - "8080:8080"
    restart: unless-stopped
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
```

## 🔒 Security Features

### Container Security
- **Non-root user**: Runs as UID 1001 (netplan user)
- **Read-only filesystem**: No write access to container filesystem
- **Dropped capabilities**: All Linux capabilities dropped
- **No new privileges**: Prevents privilege escalation
- **Minimal base image**: Alpine Linux with minimal packages

### Network Security
- **Single port exposure**: Only port 8080 exposed
- **No unnecessary services**: Only the web application runs
- **Health checks**: Monitoring for availability

## 📊 Performance

### Image Size
- **Base image**: Alpine Linux (~5MB)
- **Go binary**: ~10MB
- **Total image**: ~15MB
- **Runtime memory**: ~5-10MB

### Resource Limits

```bash
# Run with resource limits
docker run -d \
  --name netplan-generator \
  -p 8080:8080 \
  --memory=50m \
  --cpus=0.5 \
  netplan-web-generator:latest
```

## 🚀 Deployment Scenarios

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: netplan-web-generator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: netplan-web-generator
  template:
    metadata:
      labels:
        app: netplan-web-generator
    spec:
      containers:
      - name: netplan-web-generator
        image: netplan-web-generator:1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "32Mi"
            cpu: "100m"
          limits:
            memory: "64Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Docker Swarm

```bash
# Deploy to Docker Swarm
docker service create \
  --name netplan-web-generator \
  --publish 8080:8080 \
  --replicas 3 \
  --constraint 'node.role==worker' \
  netplan-web-generator:latest
```

### Behind Reverse Proxy

```yaml
# With Traefik
version: '3.8'
services:
  netplan-web-generator:
    image: netplan-web-generator:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.netplan.rule=Host(`netplan.example.com`)"
      - "traefik.http.routers.netplan.tls=true"
      - "traefik.http.routers.netplan.tls.certresolver=letsencrypt"
    networks:
      - traefik
```

## 🧪 Testing

### Container Testing

```bash
# Build and test
make docker-test

# Manual testing
docker run --rm -p 8080:8080 netplan-web-generator:latest &
curl -f http://localhost:8080/
curl -f http://localhost:8080/version
```

### Load Testing

```bash
# Using Apache Bench (if available)
ab -n 1000 -c 10 http://localhost:8080/

# Using curl for basic testing
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/
done
```

## 🔧 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker logs netplan-generator

# Check if port is available
netstat -tulpn | grep 8080

# Try different port
docker run -p 8081:8080 netplan-web-generator:latest
```

#### Health Check Failing
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' netplan-generator

# Test health endpoint manually
curl -v http://localhost:8080/
```

#### Permission Issues
```bash
# Check if running as non-root
docker exec netplan-generator id

# Check file permissions
docker exec netplan-generator ls -la /app/
```

### Debug Mode

```bash
# Run with debug output
docker run -it --rm netplan-web-generator:latest

# Access container shell (if needed for debugging)
docker run -it --rm --entrypoint /bin/sh netplan-web-generator:latest
```

## 📋 Maintenance

### Updates

```bash
# Pull latest image
docker pull netplan-web-generator:latest

# Recreate container
docker-compose up -d --force-recreate
```

### Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Complete cleanup
make docker-clean
```

### Monitoring

```bash
# Monitor resource usage
docker stats netplan-generator

# Monitor logs
docker logs -f netplan-generator

# Health monitoring
watch 'docker inspect --format="{{.State.Health.Status}}" netplan-generator'
```

## 📝 License

Copyright (C) 2025 Michael Tinsay

This container and application are licensed under the GNU General Public License v3.0.
See the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Make changes to container configuration
3. Test with `make docker-test`
4. Submit a pull request

For container-specific issues, please include:
- Docker version
- Host operating system
- Container logs
- Steps to reproduce