# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Keeps Python from generating .pyc files inside the container
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python buffering stdout so logs appear immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS-level build deps needed by some Python packages (bcrypt, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 8000

# Run Alembic migrations then start the server.
# Use sh -c so we can chain commands.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
