# Use official Python 3.12 Alpine base image for small size and latest Python
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Install system build dependencies
RUN apk add --no-cache build-base gcc libffi-dev musl-dev

# Install PDM globally (Python Development Master)
RUN pip install pdm

# Copy the full project into the container
COPY . /app

# Install only production dependencies
RUN pdm install --prod

# Set environment variable to ensure local module resolution
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Default command (can be overridden by docker run args)
CMD ["hollywood_pub_sub", "--help"]
