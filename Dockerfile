# Fraud Detection API Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (production only)
# Development dependencies are in requirements-dev.txt (not needed in production)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY configs/ ./configs/
COPY scripts/serve_model.py ./scripts/

# Copy model artifacts and feature metadata (for production deployment)
# These should be included in the deployment package
COPY models/*.joblib ./models/ 2>/dev/null || echo "No models to copy (will be mounted at runtime)"
COPY data/selected_features.json ./data/ 2>/dev/null || echo "No feature metadata to copy (will be mounted at runtime)"

# Create necessary directories for runtime
RUN mkdir -p logs data models

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the inference server
CMD ["python", "scripts/serve_model.py"]
