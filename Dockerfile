FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching — changes rarely)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and tests
COPY src/ ./src/
COPY tests/ ./tests/

# Run tests by default
CMD ["pytest", "tests/", "-v"]
