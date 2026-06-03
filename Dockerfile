# ============================================================
# Dockerfile — Container configuration for BizAnalytics
#
# This file tells Docker how to package the entire backend
# application into a portable container that can run on
# any server including Render cloud platform.
#
# Build stages:
# 1. Start from official Python image
# 2. Set working directory
# 3. Install dependencies
# 4. Copy application code
# 5. Expose port and start server
# ============================================================

# Use official Python 3.11 slim image as base
# slim = smaller size, faster download
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer)
# If requirements don't change, Docker skips reinstalling
COPY requirements.txt .

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Create the uploads directory so it exists at runtime
RUN mkdir -p data/uploads

# Tell Docker this container listens on port 5000
EXPOSE 5000

# Command to start the Flask app using gunicorn
# gunicorn is a production-grade web server
# workers=2 means 2 parallel request handlers
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --chdir backend app:app