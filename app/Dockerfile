# Use a lightweight python image
FROM python:3.11-slim

ARG GIT_SHA="unknown"
ENV APP_VERSION=$GIT_SHA

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Install the package in editable mode to enable the 'analyze' command
RUN pip install -e .

# Expose FastAPI port
EXPOSE 8000

# Default command starts the API
CMD ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
