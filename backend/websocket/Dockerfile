FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Add metadata
LABEL maintainer="Ali Nahid"
LABEL description="Websocket server to communicate logs between Backend AIAPP and Frontend"
LABEL version="1.0"

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8765

# Command to run the application
ENTRYPOINT ["python", "websocketserver.py"]