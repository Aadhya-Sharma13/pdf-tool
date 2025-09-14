# Use the official Python 3.11 image as the base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ghostscript \
    tesseract-ocr \
    poppler-utils \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Run the Flask app
CMD ["python", "app2.py"]
