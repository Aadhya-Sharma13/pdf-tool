#!/bin/bash

# Exit if any command fails
set -e

# Update package lists with sudo
sudo apt-get update

# Install system dependencies
sudo apt-get install -y ghostscript tesseract-ocr poppler-utils

# Upgrade pip and install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Run the Flask app
python app2.py
