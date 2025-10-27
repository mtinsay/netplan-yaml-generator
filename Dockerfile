# Build stage
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git

# Set working directory
WORKDIR /app

# Copy go mod files first for better caching
COPY go.mod go.sum* ./

# Download dependencies
RUN go mod download && go mod verify

# Copy only necessary Go source files
COPY main.go main_test.go ./
COPY templates/ ./templates/

# Build the application with optimizations
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -a -installsuffix cgo \
    -ldflags='-w -s -extldflags "-static"' \
    -o netplan-generator .

# Final stage - minimal Alpine image
FROM alpine:3.19

# Install minimal runtime dependencies
RUN apk --no-cache add \
    ca-certificates \
    wget \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S netplan && \
    adduser -u 1001 -S netplan -G netplan -h /app

# Set working directory
WORKDIR /app

# Copy the binary from builder stage
COPY --from=builder /app/netplan-generator ./netplan-generator

# Change ownership to non-root user
RUN chown -R netplan:netplan /app && \
    chmod +x /app/netplan-generator

# Switch to non-root user
USER netplan

# Expose port
EXPOSE 8080

# Add metadata
LABEL maintainer="Michael Tinsay" \
      version="1.0.0" \
      description="Netplan YAML Generator Web Application" \
      license="GPLv3" \
      org.opencontainers.image.source="https://github.com/mtinsay/netplan-yaml-generator" \
      org.opencontainers.image.documentation="https://github.com/mtinsay/netplan-yaml-generator/blob/main/README-golang.md"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

# Run the application
CMD ["./netplan-generator"]