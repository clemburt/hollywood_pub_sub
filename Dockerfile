# Use official Python 3.12 Alpine base image for minimal size and up-to-date Python
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Install system build dependencies for compiling packages if needed
RUN apk add --no-cache build-base gcc libffi-dev musl-dev

# Install PDM globally (Python Development Master - dependency manager)
RUN pip install pdm

# Copy the entire project into the container
COPY . /app

# Install production dependencies using PDM (without dev dependencies)
RUN pdm install --prod

# Set PYTHONPATH to include /app for module resolution
ENV PYTHONPATH=/app

# Add PDM's virtualenv bin to PATH to allow CLI execution
ENV PATH="/app/.venv/bin:$PATH"

# Use ENTRYPOINT to directly expose the CLI 'hollywood_pub_sub' installed by PDM
ENTRYPOINT ["hollywood_pub_sub"]

# Default command if none is provided - show help for the CLI
CMD ["--help"]
