#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update package lists
apt-get update

# Install Ghostscript, Tesseract OCR, and Poppler utilities
apt-get install -y ghostscript tesseract-ocr poppler-utils

# Install Python dependencies from requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Run the Flask app
python app2.py
