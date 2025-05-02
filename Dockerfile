# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/apnea_trainer /app/apnea_trainer
COPY config.toml /app/config.toml

# Run the web server
CMD ["uvicorn", "apnea_trainer.web:app", "--host", "0.0.0.0", "--port", "8000"] 