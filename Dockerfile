# Use Python 3.12 Alpine as the base image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Install system build dependencies
RUN apk add --no-cache build-base gcc libffi-dev musl-dev

# Install PDM globally
RUN pip install pdm

# Copy all project files
COPY . /app

# Install dependencies (no lock file required)
RUN pdm install --prod

# Set environment variables (optional)
ENV PYTHONPATH=/app

# Default command can be overridden
CMD ["pdm", "run", "hollywood_pub_sub", "--max_movies_per_composer", "10", "--winning_threshold", "5"]
