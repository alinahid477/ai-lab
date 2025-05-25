FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Add metadata
LABEL maintainer="Ali Nahid"
LABEL description="AI Backend REST service for Log Classification and Analysis"
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

# Create directories needed by the application
RUN mkdir -p /tmp/logs /aiapp/prompt_files

COPY prompt-files/*.txt /aiapp/prompt_files/

# Expose the port that the application runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]