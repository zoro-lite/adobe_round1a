#!/bin/bash

# Adobe Hackathon Round 1A - Build and Run Script

echo "Adobe India Hackathon - Round 1A: PDF Outline Extractor"
echo "========================================================"

# Build Docker image
echo "Building Docker image..."
docker build --platform linux/amd64 -t pdf-outline-extractor:round1a .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed!"
    exit 1
fi

echo "Docker image built successfully!"

# Create input and output directories for testing
mkdir -p input output

echo ""
echo "To run the container:"
echo "docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none pdf-outline-extractor:round1a"
echo ""
echo "Place your PDF files in the 'input' directory and the results will appear in the 'output' directory."

# Check if we have any PDFs in input directory
if [ "$(ls -A input/*.pdf 2>/dev/null)" ]; then
    echo ""
    echo "Found PDF files in input directory. Running extraction..."
    docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:round1a
    
    echo ""
    echo "Processing complete! Check the 'output' directory for results."
else
    echo ""
    echo "No PDF files found in input directory. Add some PDFs to test the extractor."
fi