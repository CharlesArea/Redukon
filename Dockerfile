# Build API server image only (connects to Ollama on host)
FROM python:3.10-slim

WORKDIR /app

# Install Redukon
RUN pip install redukon

# Create log directory
RUN mkdir -p /app/log

# Expose port
EXPOSE 8000

# Default command - runs API server
# Note: Ensure Ollama is running on host machine
CMD ["redukon", "serve", "--host", "0.0.0.0", "--port", "8000"]
