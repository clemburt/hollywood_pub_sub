# Use Python 3.12 Alpine base image
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache build-base

# Install pdm globally
RUN pip install pdm

# Copy all project files including README.md, pyproject.toml, lock file, source code, etc.
COPY . /app

# Install project dependencies without locking (use pdm.lock for reproducible installs if preferred)
RUN pdm install --no-lock

# Default command (can be overridden)
CMD ["python", "src/hollywood_pub_sub/main.py", "--api_key", "${TMDB_API_KEY}", "--max_movies_per_composer", "10", "--winning_threshold", "5"]
