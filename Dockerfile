# Use Python 3.12 Alpine as the base image
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install system build dependencies and runtime libs
RUN apk add --no-cache build-base gcc libffi-dev musl-dev

# Install PDM globally
RUN pip install --no-cache-dir pdm

# Copy project files
COPY . /app

# Install production dependencies with PDM (without dev deps)
RUN pdm install --prod

# Set PYTHONPATH for imports
ENV PYTHONPATH=/app

# Default command: run the typer CLI app
CMD ["pdm", "run", "hollywood_pub_sub", "--max_movies_per_composer", "10", "--winning_threshold", "5"]
