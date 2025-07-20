# Use Python 3.12 Alpine base image for a lightweight and up-to-date environment
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Install build dependencies required for compiling packages
RUN apk add --no-cache build-base

# Install PDM globally to manage Python dependencies and project installation
RUN pip install pdm

# Copy project files into the container
COPY . /app

# Install project dependencies without creating or using a lock file
RUN pdm install --no-lock -e .

# Default command can be overridden when running the container
CMD ["python", "src/hollywood_pub_sub/main.py", "--api_key", "${TMDB_API_KEY}", "--max_movies_per_composer", "10", "--winning_threshold", "5"]
