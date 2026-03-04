# Base image for Raspberry Pi (ARM64)
FROM arm64v8/debian:bookworm-slim

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-picamera2 \
    python3-opencv \
    python3-numpy \
    libcamera0 \
    libcamera-tools \
    libcap-dev \
    udev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application code
COPY motion-detect.py .

# Create output directories
RUN mkdir -p motion_captures/photos motion_captures/videos

# Volume for persisting captured files on the host
VOLUME ["/app/motion_captures"]

# Run the motion detection script
CMD ["python3", "motion-detect.py"]