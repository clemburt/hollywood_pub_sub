# Use Alpine-based Python 3.12 image for a small footprint
FROM python:3.12-alpine

# Set working directory inside container
WORKDIR /app

# Install system dependencies required for pdm and builds
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    curl \
    bash

# Upgrade pip and install pdm 2.x explicitly
RUN pip install --upgrade pip
RUN pip install 'pdm>=2.0.0'

# Copy project files (including pyproject.toml and pdm.lock)
COPY pyproject.toml pdm.lock /app/
COPY src /app/src

# Install dependencies without locking
RUN pdm install --no-lock

# Install package in development mode
RUN pdm develop

# Default command (can be overridden by CI or docker run)
CMD ["python", "src/hollywood_pub_sub/main.py"]
