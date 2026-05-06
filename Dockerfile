# Use Python 3.13 as base image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create directories for data
RUN mkdir -p /app/chroma_db /app/mlflow_data

# Expose port for FastAPI
EXPOSE 8000

# Command to run Livingstone
CMD ["uvicorn", "livingstone_server:app", "--host", "0.0.0.0", "--port", "8000"]
