FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8000

# Use exec form and handle PORT env var
CMD exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} 