# Netplan Web Generator Makefile
# Copyright (C) 2025 Michael Tinsay

.PHONY: build run test clean docker docker-run docker-stop help

# Variables
BINARY_NAME=netplan-generator
DOCKER_IMAGE=netplan-web-generator
PORT=8080

# Default target
help: ## Show this help message
	@echo "Netplan Web Generator - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the application binary
	@echo "Building $(BINARY_NAME)..."
	go build -o $(BINARY_NAME) .
	@echo "Build complete: $(BINARY_NAME)"

build-linux: ## Build for Linux (useful for containers)
	@echo "Building $(BINARY_NAME) for Linux..."
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o $(BINARY_NAME)-linux .
	@echo "Linux build complete: $(BINARY_NAME)-linux"

run: ## Run the application locally
	@echo "Starting $(BINARY_NAME) on port $(PORT)..."
	go run main.go

test: ## Test the application
	@echo "Testing application..."
	go test -v ./...
	@echo "Testing web endpoints..."
	@if command -v curl >/dev/null 2>&1; then \
		echo "Starting server in background..."; \
		go run main.go & \
		SERVER_PID=$$!; \
		sleep 2; \
		echo "Testing GET /"; \
		curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:$(PORT)/; \
		echo "Testing POST /generate"; \
		curl -s -o /dev/null -w "Status: %{http_code}\n" -X POST http://localhost:$(PORT)/generate -d "interface_type=ethernet&interface_name=eth0&renderer=networkd"; \
		kill $$SERVER_PID; \
		echo "Tests completed"; \
	else \
		echo "curl not available, skipping endpoint tests"; \
	fi

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -f $(BINARY_NAME) $(BINARY_NAME)-linux $(BINARY_NAME)-windows.exe $(BINARY_NAME)-darwin
	@echo "Clean complete"

docker: ## Build Docker image
	@echo "Building Docker image: $(DOCKER_IMAGE)..."
	docker build -t $(DOCKER_IMAGE):latest -t $(DOCKER_IMAGE):1.0.0 .
	@echo "Docker image built: $(DOCKER_IMAGE)"

docker-run: docker ## Build and run Docker container
	@echo "Running Docker container on port $(PORT)..."
	docker run -d --name $(DOCKER_IMAGE) -p $(PORT):8080 $(DOCKER_IMAGE):latest
	@echo "Container started. Access at http://localhost:$(PORT)"
	@echo "To stop: make docker-stop"

docker-stop: ## Stop and remove Docker container
	@echo "Stopping Docker container..."
	-docker stop $(DOCKER_IMAGE)
	-docker rm $(DOCKER_IMAGE)
	@echo "Container stopped and removed"

docker-build-optimized: ## Build optimized Docker image with build script
	@echo "Building optimized Docker image..."
	@if [ -f "build-container.sh" ]; then \
		bash build-container.sh; \
	else \
		echo "build-container.sh not found, using regular docker build"; \
		make docker; \
	fi

docker-test: docker ## Build and test Docker container
	@echo "Testing Docker container..."
	docker run --rm -p 8080:8080 -d --name test-$(DOCKER_IMAGE) $(DOCKER_IMAGE):latest
	@sleep 3
	@if command -v curl >/dev/null 2>&1; then \
		echo "Testing health endpoint..."; \
		curl -s -f http://localhost:8080/ > /dev/null && echo "✅ Health check passed" || echo "❌ Health check failed"; \
	else \
		echo "curl not available, skipping health test"; \
	fi
	@docker stop test-$(DOCKER_IMAGE)
	@echo "Test completed"

docker-size: ## Show Docker image size
	@echo "Docker image sizes:"
	@docker images $(DOCKER_IMAGE) --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

docker-clean: ## Clean up Docker images and containers
	@echo "Cleaning up Docker resources..."
	-docker stop $(DOCKER_IMAGE) test-$(DOCKER_IMAGE)
	-docker rm $(DOCKER_IMAGE) test-$(DOCKER_IMAGE)
	-docker rmi $(DOCKER_IMAGE):latest $(DOCKER_IMAGE):1.0.0
	@echo "Docker cleanup completed"

docker-compose-up: ## Start with docker-compose
	@echo "Starting with docker-compose..."
	docker-compose up -d
	@echo "Service started. Access at http://localhost:$(PORT)"

docker-compose-down: ## Stop docker-compose services
	@echo "Stopping docker-compose services..."
	docker-compose down
	@echo "Services stopped"

install: build ## Install the binary to system PATH
	@echo "Installing $(BINARY_NAME) to /usr/local/bin..."
	sudo cp $(BINARY_NAME) /usr/local/bin/
	@echo "Installation complete"

uninstall: ## Remove the binary from system PATH
	@echo "Removing $(BINARY_NAME) from /usr/local/bin..."
	sudo rm -f /usr/local/bin/$(BINARY_NAME)
	@echo "Uninstallation complete"

dev: ## Run in development mode with auto-reload (requires air)
	@if command -v air >/dev/null 2>&1; then \
		echo "Starting development server with auto-reload..."; \
		air; \
	else \
		echo "air not installed. Install with: go install github.com/cosmtrek/air@latest"; \
		echo "Falling back to regular run..."; \
		make run; \
	fi

format: ## Format Go code
	@echo "Formatting Go code..."
	go fmt ./...
	@echo "Code formatted"

lint: ## Run linter (requires golangci-lint)
	@if command -v golangci-lint >/dev/null 2>&1; then \
		echo "Running linter..."; \
		golangci-lint run; \
	else \
		echo "golangci-lint not installed. Install from: https://golangci-lint.run/usage/install/"; \
	fi

deps: ## Download dependencies
	@echo "Downloading dependencies..."
	go mod download
	go mod tidy
	@echo "Dependencies updated"

# Cross-platform builds
build-all: ## Build for all platforms
	@echo "Building for all platforms..."
	GOOS=linux GOARCH=amd64 go build -o $(BINARY_NAME)-linux-amd64 .
	GOOS=windows GOARCH=amd64 go build -o $(BINARY_NAME)-windows-amd64.exe .
	GOOS=darwin GOARCH=amd64 go build -o $(BINARY_NAME)-darwin-amd64 .
	GOOS=darwin GOARCH=arm64 go build -o $(BINARY_NAME)-darwin-arm64 .
	@echo "Cross-platform builds complete"

release: clean build-all docker ## Prepare release artifacts
	@echo "Creating release directory..."
	mkdir -p release
	mv $(BINARY_NAME)-* release/
	@echo "Release artifacts ready in ./release/"

info: ## Show project information
	@echo "Netplan Web Generator"
	@echo "Copyright (C) 2025 Michael Tinsay"
	@echo "Licensed under GPLv3"
	@echo ""
	@echo "Go version: $$(go version)"
	@echo "Project: $$(pwd)"
	@echo "Binary: $(BINARY_NAME)"
	@echo "Docker image: $(DOCKER_IMAGE)"
	@echo "Default port: $(PORT)"