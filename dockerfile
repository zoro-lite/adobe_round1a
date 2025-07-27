# Use Python 3.9 slim image for AMD64
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY main.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Make script executable
RUN chmod +x main.py

# Set the default command
CMD ["python", "main.py"]