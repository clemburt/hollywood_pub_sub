# Use python 3.12 slim-alpine base image for smaller size and security
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install dependencies for pdm and build tools
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    curl \
    bash

# Install pdm (latest stable)
RUN pip install --upgrade pip \
    && pip install pdm

# Copy only necessary files for installing deps
COPY pyproject.toml pdm.lock /app/

# Install project dependencies
RUN pdm install --no-lock

# Copy full source code
COPY src /app/src
COPY scripts /app/scripts
COPY tests /app/tests

# Install your package in editable mode
RUN pdm develop

# Default command (can be overridden in CI or docker run)
CMD ["pdm", "run", "python", "-m", "hollywood_pub_sub.main"]
