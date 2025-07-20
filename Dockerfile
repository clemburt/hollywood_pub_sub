# Use official Python 3.12 Alpine base image for minimal size and latest Python
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apk add --no-cache build-base gcc libffi-dev musl-dev

# Install PDM globally for dependency management
RUN pip install pdm

# Copy the entire project into the container
COPY . /app

# Install production dependencies via PDM (skip dev dependencies)
RUN pdm install --prod

# Ensure Python modules are discoverable inside /app
ENV PYTHONPATH=/app

# Include PDM's virtual environment bin folder in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Use ENTRYPOINT to make the CLI command the container's default executable
# So users can run `docker run image run --api_key ...`
ENTRYPOINT ["hollywood_pub_sub"]

# Default CMD: show CLI help when no arguments are passed
CMD ["--help"]
