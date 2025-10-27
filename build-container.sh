#!/bin/bash
#
# Build script for Netplan Web Generator container
# Copyright (C) 2025 Michael Tinsay
# Licensed under GPLv3
#

set -e

# Parse command line arguments
DEBUG=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -D|--debug)
            DEBUG=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -D, --debug    Enable debug mode (set -x)"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Enable debug mode if requested
if [[ "$DEBUG" == "true" ]]; then
    echo -e "${YELLOW}🐛 Debug mode enabled${NC}"
    set -x
fi

# Configuration
IMAGE_NAME="netplan-web-generator"
VERSION="1.0.0"
REGISTRY=""  # Set this if pushing to a registry

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Building Netplan Web Generator Container${NC}"
echo -e "${BLUE}============================================${NC}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "main.go" ]]; then
    echo -e "${RED}❌ main.go not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Clean up any existing binary
echo -e "${YELLOW}🧹 Cleaning up existing binaries...${NC}"
rm -f netplan-generator netplan-generator.exe

# Build the Docker image
echo -e "${YELLOW}🔨 Building Docker image: ${IMAGE_NAME}:${VERSION}${NC}"
docker build \
    --tag "${IMAGE_NAME}:${VERSION}" \
    --tag "${IMAGE_NAME}:latest" \
    --label "build.date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --label "build.version=${VERSION}" \
    --label "vcs.ref=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    .

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

# Show image information
echo -e "${BLUE}📊 Image Information:${NC}"
docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Test the container
echo -e "${YELLOW}🧪 Testing container...${NC}"
CONTAINER_ID=$(docker run -d -p 8080:8080 "${IMAGE_NAME}:${VERSION}")
CONTAINER_ID_SHORT=${CONTAINER_ID:0:12}

# Wait for container to start
echo -e "${YELLOW}⏳ Waiting 10 seconds for container to start...${NC}"
sleep 10

# Check if container is running
if docker ps | grep -q "${CONTAINER_ID_SHORT}"; then
    echo -e "${GREEN}✅ Container is running successfully!${NC}"
    
    # Test health endpoint
    if command -v curl &> /dev/null; then
        echo -e "${YELLOW}🔍 Testing health endpoint...${NC}"
        if curl -s -f http://localhost:8080/ > /dev/null; then
            echo -e "${GREEN}✅ Health check passed!${NC}"
        else
            echo -e "${YELLOW}⚠️  Health check failed (container might still be starting)${NC}"
        fi
    fi
    
    # Stop test container
    docker stop "${CONTAINER_ID_SHORT}" > /dev/null
    docker rm "${CONTAINER_ID_SHORT}" > /dev/null
    echo -e "${GREEN}✅ Test container cleaned up${NC}"
else
    echo -e "${RED}❌ Container failed to start!${NC}"
    docker logs "${CONTAINER_ID_SHORT}"
    docker rm "${CONTAINER_ID_SHORT}" > /dev/null
    exit 1
fi

echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo -e "${BLUE}📋 Usage:${NC}"
echo -e "  Run container:     ${YELLOW}docker run -p 8080:8080 ${IMAGE_NAME}:${VERSION}${NC}"
echo -e "  With docker-compose: ${YELLOW}docker-compose up -d${NC}"
echo -e "  Access web app:    ${YELLOW}http://localhost:8080${NC}"

# Optional: Push to registry
if [[ -n "${REGISTRY}" ]]; then
    echo -e "${YELLOW}📤 Pushing to registry: ${REGISTRY}${NC}"
    docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:latest"
    docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    docker push "${REGISTRY}/${IMAGE_NAME}:latest"
    echo -e "${GREEN}✅ Pushed to registry successfully!${NC}"
fi

echo -e "${BLUE}🏁 All done!${NC}"