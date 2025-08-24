# Dockerfile for Drone Vision AirSim Project
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY settings.json .
COPY README.md .

# Create necessary directories
RUN mkdir -p models data docs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV AIRSIM_HOST=host.docker.internal
ENV AIRSIM_PORT=41451

# Expose port for potential web interface
EXPOSE 8080

# Default command
CMD ["python", "src/main.py"]
