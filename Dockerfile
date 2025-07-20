# Use official Python 3.12 based on Alpine (lightweight)
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Install required system dependencies for building packages (e.g. wheels)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy the project files into the container
COPY pyproject.toml pdm.lock ./
COPY src/ ./src/

# Install PDM (Python Dependency Manager)
RUN pip install --no-cache-dir pdm

# Install Python dependencies in isolated environment (no virtualenv)
RUN pdm install --no-editable --prod

# Set environment variable for unbuffered logging (useful for CI output)
ENV PYTHONUNBUFFERED=1

# Optionally define the default command to run the app (can be overridden)
CMD ["python", "src/hollywood_pub_sub/main.py"]
